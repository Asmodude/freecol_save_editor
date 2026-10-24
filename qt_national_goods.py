"""Pure read-only aggregation of stored warehouse goods for a colonial player."""
from collections import Counter
import xml.etree.ElementTree as ET
import presentation


def national_goods(document, player_id):
    if not player_id or player_id not in document.players:
        return []
    totals=Counter()
    colonies=Counter()
    catalog=set(getattr(document,'goods_types',()) or ())
    for colony in document.colonies:
        if colony.get('owner')!=player_id:
            continue
        present=set()
        for good in colony.findall('./goodsContainer/storedGoods/goods'):
            kind=good.get('type')
            if not kind:
                continue
            catalog.add(kind)
            raw=good.get('amount','0')
            try:
                amount=int(raw)
            except ValueError:
                continue
            totals[kind]+=amount
            if amount>0:
                present.add(kind)
        colonies.update(present)
    return [ET.Element('nationalGoodsView', {
        'id':kind, 'name':presentation.readable(kind),
        'amount':str(totals[kind]), 'colonies':str(colonies[kind]),
        'owner':player_id})
        for kind in sorted(catalog,key=lambda k:presentation.readable(k).casefold())]


def transported_goods_breakdown(document, player_id, goods_id):
    """Cargo in authoritative owned units only; never count colony warehouses."""
    if not player_id or player_id not in document.players or not goods_id:
        return []
    rows=[]
    for unit in document.units:
        if unit.get('owner') != player_id:
            continue
        amount=0
        # FreeCol cargo can be in a unit's goodsContainer/storedGoods.
        for good in unit.findall('./goodsContainer/storedGoods/goods'):
            if good.get('type') == goods_id:
                try:
                    amount += int(good.get('amount','0'))
                except ValueError:
                    continue
        if amount:
            rows.append((unit.get('id') or 'Unknown unit',
                         presentation.readable(unit.get('unitType')),
                         document.location_name(unit.get('location')),
                         str(amount)))
    return sorted(rows,key=lambda row:row[0])

def colony_goods_breakdown(document, player_id, goods_id):
    """Stable, read-only per-colony quantities including zero-stock colonies."""
    if not player_id or player_id not in document.players or not goods_id:
        return []
    rows=[]
    for colony in document.colonies:
        if colony.get('owner')!=player_id:
            continue
        total=0
        for good in colony.findall('./goodsContainer/storedGoods/goods'):
            if good.get('type')==goods_id:
                try:
                    total+=int(good.get('amount','0'))
                except ValueError:
                    continue
        rows.append((colony.get('name') or colony.get('id') or 'Unnamed colony',
                     str(total)))
    return sorted(rows,key=lambda row:row[0].casefold())
