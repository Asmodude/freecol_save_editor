"""Phase 1 unit navigation groups, based only on authoritative saved locations.

Every owned unit is assigned exactly once; uncertain locations go to Other units.
"""
def unit_groups(document, owner):
    owned=[u for u in document.units if u.get('owner')==owner]
    colonies=[c for c in document.colonies if c.get('owner')==owner and c.get('id')]
    direct={}
    workers={}
    for colony in colonies:
        for key in (colony.get('id'),colony.get('tile')):
            if key:
                direct[key]=colony.get('id')
        for unit in colony.iter('unit'):
            if unit.get('id'):
                workers[unit.get('id')]=colony.get('id')
    ships={u.get('id') for u in owned if u.get('id') and
           (u.get('unitType') or '').rsplit('.',1)[-1] in
           {'caravel','merchantman','galleon','privateer','frigate','manOWar'}}
    result={('colony',c.get('id')):[] for c in colonies}
    result[('ship','')]=[]
    for ship_id in ships:
        result[('vessel',ship_id)]=[]
    result[('other','')]=[]
    for unit in owned:
        uid=unit.get('id')
        location=unit.get('location')
        colony_id=workers.get(uid) or direct.get(location)
        if colony_id:
            key=('colony',colony_id)
        elif location in ships:
            key=('vessel',location)
        else:
            key=('other','')
        result[key].append(unit)
        if key[0]=='vessel':
            result[('ship','')].append(unit)
    return result


def unit_group_scope(owner, kind, target=''):
    return 'unit-group|' + owner + '|' + kind + '|' + target


def scoped_units(document, scope):
    parts=scope.split('|',3)
    if len(parts)!=4 or parts[0]!='unit-group':
        return []
    _,owner,kind,target=parts
    if kind not in ('colony','ship','vessel','other'):
        return []
    return unit_groups(document,owner).get((kind,target),[])
