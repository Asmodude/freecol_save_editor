"""Read-only diplomacy from saved player stance/tension and settlement alarm nodes."""
from xml.etree.ElementTree import Element

def diplomacy_rows(document, owner_id):
    """One saved-state record per counterpart; stance and tension in columns."""
    owner=document.players.get(owner_id)
    if owner is None:
        return []
    result=[]
    for other_id,other in document.players.items():
        if other_id==owner_id:
            continue
        category=('Rival Nations' if other.get('playerType')=='colonial' else
                  'Natives' if other.get('playerType') in ('indian','native') else 'Other')
        if category=='Other':
            continue
        saved={}
        for kind in ('stance','tension'):
            node=next((c for c in owner.findall(kind) if c.get('player')==other_id),None)
            saved[kind]=node.get('value','(absent)') if node is not None else '(absent)'
        result.append(Element('diplomacyView',{
            'id':other_id, 'owner':owner_id, 'other':other_id,
            'nation':other.get('username') or other_id,
            'category':category,'stance':saved['stance'],'tension':saved['tension']}))
    return result

def settlement_alarm_rows(document, settlement):
    result=[]
    for other_id,other in document.players.items():
        if other.get('playerType')!='colonial':
            continue
        saved=next((c for c in settlement.findall('alarm') if c.get('player')==other_id),None)
        result.append((other.get('username') or other_id,
                       saved.get('value','(absent)') if saved is not None else '(absent)'))
    return result
