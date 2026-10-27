"""Read-only colony detail data extracted from authoritative FreeCol colony XML.

No GUI imports and no changes to savegame data.
"""
import presentation
from qt_special_resources import is_warehouse_good


def goods_catalog(colony, document):
    """Ruleset goods plus saved goods; preserve stable identifiers for future edits."""
    stored = colony.find('./goodsContainer/storedGoods')
    by_type = {}
    if stored is not None:
        for item in stored.findall('goods'):
            goods_type = item.get('type')
            if is_warehouse_good(goods_type):
                by_type[goods_type] = item
    available = set(by_type)
    if document is not None:
        available.update(kind for kind in (getattr(document, 'goods_types', ()) or ())
                         if is_warehouse_good(kind))
    return [(kind, by_type.get(kind)) for kind in
            sorted(available, key=lambda key: presentation.readable(key).casefold())]


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
    goods=[(presentation.readable(kind), node.get('amount','0') if node is not None else '0')
           for kind, node in goods_catalog(colony, document)]
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
    # None marks an absent XML node displayed as zero: Phase 2 must create it.
    goods=[node for _, node in goods_catalog(colony, document)]
    return {'Buildings':buildings,'Workers':workers,
            'Stationed units':stationed,'Goods':goods}
