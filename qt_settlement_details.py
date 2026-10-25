"""Read-only authoritative native-settlement unit affiliation.

Native settlements do not have colony tile/building workers. Affiliation follows
the accepted Tk editor: home settlement ID or an explicit ownedUnits reference.
"""
import presentation


def settlement_units(settlement, document):
    sid=settlement.get('id')
    owner=settlement.get('owner')
    owned={node.get('id') for node in settlement.findall('ownedUnits') if node.get('id')}
    rows=[]
    for unit in document.units:
        uid=unit.get('id')
        if not uid or unit.get('owner')!=owner:
            continue
        if unit.get('indianSettlement')!=sid and uid not in owned:
            continue
        rows.append((uid,
                     presentation.readable(unit.get('unitType')),
                     document.location_name(unit.get('location')),
                     document.location_name(unit.get('indianSettlement')),
                     presentation.readable(unit.get('role'))))
    return ('ID','Unit type','Current location','Home settlement','Role'),rows
