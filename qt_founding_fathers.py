"""Read-only FreeCol Founding Father membership, following Player XML serialization."""
import xml.etree.ElementTree as ET
import presentation


def _list_ids(player, tag):
    node=player.find(tag)
    if node is None:
        return []
    keys=sorted((k for k in node.attrib if k.startswith('x') and k[1:].isdigit()),
                key=lambda k:int(k[1:]))
    return [node.get(k) for k in keys if node.get(k)]


def father_rows(player):
    """One non-mutating display record per known father and status."""
    acquired=_list_ids(player,'foundingFathers')
    offered=_list_ids(player,'offeredFathers')
    current=player.get('currentFather')
    statuses={}
    for father in offered:
        statuses[father]='Offered'
    if current:
        statuses[current]='Recruiting'
    for father in acquired:
        statuses[father]='Recruited'
    rows=[]
    for father,status in sorted(statuses.items(),key=lambda pair:presentation.readable(pair[0]).casefold()):
        row=ET.Element('foundingFatherView',{'id':father,'name':presentation.readable(father),
                                           'status':status,'owner':player.get('id','')})
        rows.append(row)
    return rows
