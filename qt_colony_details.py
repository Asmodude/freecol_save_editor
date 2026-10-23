"""Read-only colony detail data extracted from authoritative FreeCol colony XML.

No GUI imports and no changes to savegame data.
"""
import presentation


def colony_sections(colony, document):
    """Return explicit table headings and rows for the colony's detail tabs."""
    buildings=[]
    for building in colony.findall('building'):
        raw=building.get('buildingType','')
        short=raw.rsplit('.',1)[-1]
        category,tier=presentation.building_tier(short)
        buildings.append((presentation.readable(raw),category,tier,
                          str(len(building.findall('unit')))))
    workers=[]
    working_ids=set()
    # Units nested in a building or colonyTile are assigned to work there.
    for workplace in colony.iter():
        if workplace.tag not in ('building', 'colonyTile'):
            continue
        workplace_label=(workplace.get('buildingType') if workplace.tag=='building'
                         else workplace.get('workTile') or workplace.get('tile') or 'Colony tile')
        for unit in workplace.findall('unit'):
            uid=unit.get('id')
            if uid and uid not in working_ids:
                working_ids.add(uid)
                workers.append((uid, presentation.readable(unit.get('unitType')),
                                presentation.readable(workplace_label),
                                presentation.readable(unit.get('workType')),
                                unit.get('experience','')))
    stationed=[]
    if document is not None:
        for unit in document.units:
            uid=unit.get('id')
            if (not uid or uid in working_ids
                    or unit.get('owner')!=colony.get('owner')
                    or unit.get('location') not in (colony.get('id'),colony.get('tile'))):
                continue
            stationed.append((uid,presentation.readable(unit.get('unitType')),
                              document.location_name(unit.get('location')),
                              presentation.readable(unit.get('role')),
                              unit.get('state','')))
    goods=[]
    store=colony.find('./goodsContainer/storedGoods')
    if store is not None:
        for item in store.findall('goods'):
            goods.append((presentation.readable(item.get('type')),
                          item.get('amount','0')))
    return {
        'Buildings': (('Building','Upgrade chain','Tier','Workers'),buildings),
        'Workers': (('ID','Unit type','Workplace','Produces','Experience'),workers),
        'Stationed units': (('ID','Unit type','Location','Role','State'),stationed),
        'Goods': (('Goods','Amount'),goods),
    }

def colony_detail_nodes(colony, document):
    """Source XML element for each displayed detail row, in matching row order.

    The same traversal/order as colony_sections. These are references only.
    """
    buildings=list(colony.findall('building'))
    workers=[]
    seen=set()
    for workplace in colony.iter():
        if workplace.tag not in ('building','colonyTile'):
            continue
        for unit in workplace.findall('unit'):
            uid=unit.get('id')
            if uid and uid not in seen:
                seen.add(uid)
                workers.append(document.unit_by_id(uid) if document is not None
                               and document.unit_by_id(uid) is not None else unit)
    stationed=[]
    if document is not None:
        for unit in document.units:
            uid=unit.get('id')
            if (uid and uid not in seen and unit.get('owner')==colony.get('owner')
                    and unit.get('location') in (colony.get('id'),colony.get('tile'))):
                stationed.append(unit)
    store=colony.find('./goodsContainer/storedGoods')
    goods=list(store.findall('goods')) if store is not None else []
    return {'Buildings':buildings,'Workers':workers,
            'Stationed units':stationed,'Goods':goods}
