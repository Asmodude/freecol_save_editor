"""Pure presentation helpers for the existing FreeCol Tk interface.

The functions here intentionally retain the v0.6.2.6.4 text and tuple shapes.
"""
import re
import xml.etree.ElementTree as ET
from movement_rules import movement_cap, UnknownMovement
from location_names import location_label


def short(value):
    return (value or '').replace('model.unit.','').replace('model.role.','').replace('model.nation.','').replace('model.goods.','')


def readable(value):
    if not value:
        return ''
    value=value.rsplit('.',1)[-1]
    return re.sub(r'(?<!^)(?=[A-Z])',' ',value).replace('_',' ').title()


def experience_towards(attrs):
    goods=(attrs.get('experienceType') or '')
    if not goods:
        return '—'
    known={'lumber':'Expert Lumberjack','food':'Expert Farmer / Fisherman','cotton':'Expert Cotton Planter','tobacco':'Expert Tobacco Planter','sugar':'Expert Sugar Planter','furs':'Expert Fur Trapper','ore':'Expert Ore Miner','silver':'Expert Silver Miner'}
    key=goods.rsplit('.',1)[-1]
    return known.get(key, f'{key.title()} (experience)')


def building_tier(name):
    chains=(('stockade','fort','fortress'),('carpenterHouse','lumberMill'),('schoolhouse','college','university'),('chapel','church','cathedral'),('blacksmithHouse','blacksmithShop','ironWorks'),('tobacconistHouse','tobacconistShop','cigarFactory'),('weaverHouse','weaverShop','textileMill'),('rumDistillery','rumFactory'),('furTraderHouse','furTraderShop','furFactory'),('warehouse','warehouseExpansion'),('printingPress','newspaper'))
    for chain in chains:
        if name in chain:
            return readable(chain[0]), f'{chain.index(name)+1}/{len(chain)}'
    return 'Standalone','—'


def owner_name(key, doc):
    return doc.players[key].get('username','') if key in doc.players else (key or '')


def loc_name(key, doc):
    return location_label(key, doc.locations, doc.tiles, doc.colony_tile_names, doc.unit_locations)


def row_values(group, e, doc, session):
    a=e.attrib
    staged=session.edits
    if group=='Players':
        return (a.get('id'),a.get('username'),short(a.get('nationId')),a.get('playerType'),doc.colony_counts.get(a.get('id'),0),doc.native_counts.get(a.get('id'),0),'N/A' if a.get('gold')=='-2147483648' else staged.get((a.get('id'),'gold'),(None,a.get('gold')))[1],staged.get((a.get('id'),'tax'),(None,a.get('tax')))[1],a.get('score'),a.get('ai'),a.get('dead'))
    if group=='Colonies':
        return (a.get('id'),a.get('name'),owner_name(a.get('owner'),doc),loc_name(a.get('tile'),doc),a.get('established'),a.get('liberty'),staged.get((a.get('id'),'sonsOfLibertyTarget'),(None,a.get('sonsOfLiberty')))[1],a.get('productionBonus'))
    if group=='Native settlements':
        wanted=', '.join(short(a.get('wantedGoods'+str(i))) for i in range(3) if a.get('wantedGoods'+str(i)))
        return (a.get('id'),a.get('name'),owner_name(a.get('owner'),doc),loc_name(a.get('tile'),doc),short(a.get('learnableSkill')),wanted)
    equipment=staged.get((a.get('id'),'equipment'))
    move_unit=e
    if equipment:
        move_unit=ET.Element('unit',dict(a,role=equipment[1][0],roleCount=str(equipment[1][1])))
    try:
        maximum=movement_cap(doc.root,move_unit)
    except (UnknownMovement,TypeError):
        maximum='—'
    return (a.get('id'),short(a.get('unitType')),owner_name(a.get('owner'),doc),loc_name(a.get('location'),doc),short(staged.get((a.get('id'),'equipment'),(None,(a.get('role','model.role.default'),1)))[1][0]),experience_towards(a),staged.get((a.get('id'),'experience'),(None,a.get('experience')))[1],staged.get((a.get('id'),'movesLeft'),(None,a.get('movesLeft')))[1],maximum,a.get('hitPoints'),a.get('state'))
