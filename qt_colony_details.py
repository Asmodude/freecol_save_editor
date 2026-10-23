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
    for unit in colony.iter('unit'):
        uid=unit.get('id')
        if uid:
            workers.append((uid,presentation.readable(unit.get('unitType')),
                            presentation.readable(unit.get('workType') or unit.get('role')),
                            unit.get('experience','')))
    goods=[]
    store=colony.find('./goodsContainer/storedGoods')
    if store is not None:
        for item in store.findall('goods'):
            goods.append((presentation.readable(item.get('type')),
                          item.get('amount','0')))
    return {
        'Buildings': (('Building','Upgrade chain','Tier','Workers'),buildings),
        'Units': (('ID','Unit type','Assignment','Experience'),workers),
        'Goods': (('Goods','Amount'),goods),
    }
