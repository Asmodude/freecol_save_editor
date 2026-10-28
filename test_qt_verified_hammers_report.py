"""OC-001 Hammers report import contract and read-only Overview."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from xml.etree.ElementTree import fromstring

from qt_hammer_probe import HammerProbeError, read_verified_report
from qt_overview import record_overview


class VerifiedHammersTests(unittest.TestCase):
    def test_report_must_match_exact_save_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            save = Path(directory) / 'game.fsg'
            report = Path(directory) / 'hammers.json'
            save.write_bytes(b'source-data')
            colony = fromstring('<colony id="colony:1" owner="player:19" name="Taphus"/>')
            doc = SimpleNamespace(path=save, colonies=[colony])
            probe = ('FREECOL_HAMMERS_V2\tcolony_id\towner_id\tgross\tnet\tcolony_name\tnation_id'
                     '\ncolony:1\tplayer:19\t12\t12\tTaphus\tmodel.nation.danish\n')
            payload = {'format': 'FREECOL_HAMMERS_REPORT_V1',
                       'save_sha256': hashlib.sha256(b'source-data').hexdigest(),
                       'probe_output': probe}
            report.write_text(json.dumps(payload), encoding='utf-8')
            self.assertEqual(read_verified_report(report, doc)['colony:1'].gross, 12)
            save.write_bytes(b'different-source-data')
            with self.assertRaisesRegex(HammerProbeError, 'different save'):
                read_verified_report(report, doc)

    def test_default_no_production_data_means_unavailable(self):
        # No external FreeCol output may ever be interpreted as zero.
        source = Path(__file__).resolve().parent.joinpath('qt_overview.py').read_text(encoding='utf-8')
        self.assertIn('Unavailable — import a verified FreeCol production report', source)
        self.assertIn("getattr(document, 'hammer_production', {})", source)


if __name__ == '__main__':
    unittest.main()
