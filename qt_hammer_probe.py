"""Read-only output contract for the optional FreeCol Java production bridge.

Do not invoke Java or touch the save automatically. UI may display numbers
only when the user explicitly opts in and supplies verified probe output.
"""
from dataclasses import dataclass


class HammerProbeError(ValueError):
    pass


@dataclass(frozen=True)
class HammerProduction:
    colony_id: str
    owner_id: str
    gross: int
    net: int


_HEADER = 'FREECOL_HAMMERS_V1\tcolony_id\towner_id\tgross\tnet'
_HEADER_V2 = 'FREECOL_HAMMERS_V2\tcolony_id\towner_id\tgross\tnet\tcolony_name\tnation_id'


def parse_hammer_probe(raw: str, document):
    """Validate a full, explicitly obtained result against the loaded save."""
    if not isinstance(raw, str):
        raise HammerProbeError('Production output must be text')
    lines = raw.splitlines()
    if not lines or lines[0] not in (_HEADER, _HEADER_V2):
        raise HammerProbeError('Unsupported FreeCol production output format')
    v2 = lines[0] == _HEADER_V2
    colonies = {}
    for colony in document.colonies:
        cid = colony.get('id')
        if not cid or cid in colonies:
            raise HammerProbeError('Duplicate or missing colony identity in save')
        colonies[cid] = colony
    result = {}
    for line in lines[1:]:
        fields = line.split('\t')
        if len(fields) != (6 if v2 else 4):
            raise HammerProbeError('Malformed production row')
        colony_id, owner_id, gross_raw, net_raw = fields[:4]
        if v2 and (not fields[4] or not fields[5]):
            raise HammerProbeError('Missing colony name or nation ID')
        if colony_id not in colonies or colony_id in result:
            raise HammerProbeError('Unknown or duplicated colony in production output')
        if owner_id != colonies[colony_id].get('owner'):
            raise HammerProbeError('Production output owner does not match save')
        if not gross_raw.isascii() or not gross_raw.isdecimal():
            raise HammerProbeError('Invalid gross production')
        if net_raw.startswith('-'):
            valid_net = net_raw[1:].isascii() and net_raw[1:].isdecimal()
        else:
            valid_net = net_raw.isascii() and net_raw.isdecimal()
        if not valid_net:
            raise HammerProbeError('Invalid net production')
        gross, net = int(gross_raw), int(net_raw)
        if gross > 2_147_483_647 or abs(net) > 2_147_483_647:
            raise HammerProbeError('Production value outside supported range')
        result[colony_id] = HammerProduction(colony_id, owner_id, gross, net)
    if result.keys() != colonies.keys():
        raise HammerProbeError('Production output omits colonies from loaded save')
    return result


def read_verified_report(report_path, document):
    """Import explicit JSON report only for an identical source save."""
    import json
    import re
    from pathlib import Path
    try:
        report = json.loads(Path(report_path).read_text(encoding='utf-8'))
        if not isinstance(report, dict):
            raise HammerProbeError('Hammers report must be a JSON object')
        if report.get('format') != 'FREECOL_HAMMERS_REPORT_V1':
            raise HammerProbeError('Unsupported Hammers report')
        digest = getattr(document, 'source_sha256', None)
        if not isinstance(digest, str):
            raise HammerProbeError('Loaded save has no source checksum')
        if not isinstance(report.get('save_sha256'), str) or not re.fullmatch(r'[0-9a-f]{64}', report['save_sha256']):
            raise HammerProbeError('Missing or invalid source checksum')
        if not isinstance(report.get('probe_output'), str):
            raise HammerProbeError('Production output must be text')
        if report['save_sha256'] != digest:
            raise HammerProbeError('Production report belongs to a different save')
        return parse_hammer_probe(report['probe_output'], document)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        if isinstance(exc, HammerProbeError):
            raise
        raise HammerProbeError('Could not verify Hammers report') from exc
