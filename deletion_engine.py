"""Conservative byte-preserving FreeCol removal machinery. Reject unknown links."""
import re
import xml.etree.ElementTree as ET

class UnsafeDeletion(ValueError): pass

def _element_spans(xml, tag, identifier):
    start_pat=rb'<'+tag.encode()+rb'\b[^>]*\bid="'+re.escape(identifier.encode())+rb'"[^>]*>'
    spans=[]
    for m in re.finditer(start_pat, xml, re.S):
        end=xml.find(b'</'+tag.encode()+b'>',m.end())
        if end<0:raise UnsafeDeletion('Unclosed '+tag)
        spans.append((m.start(),end+len(tag)+3))
    return spans

def _apply_spans(xml,spans):
    spans=sorted(set(spans))
    for (_,end),(next_start,_) in zip(spans,spans[1:]):
        if end>next_start:raise UnsafeDeletion('Overlapping removal spans')
    for a,b in reversed(spans):xml=xml[:a]+xml[b:]
    return xml

def remove_unit(xml,uid,allow_settlement=None):
    if not re.fullmatch(r'unit:\d+',uid):raise UnsafeDeletion('Invalid unit id')
    root=ET.fromstring(xml);parent={c:p for p in root.iter() for c in p}
    units=[u for u in root.iter('unit') if u.get('id')==uid]
    if len(units)!=1:raise UnsafeDeletion('Expected one actual unit, found '+str(len(units)))
    unit=units[0]
    if allow_settlement:
        owner=next((x for x in root.findall('./game/map/tile/indianSettlement') if x.get('id')==allow_settlement),None)
        if owner is None or owner.get('owner')!=unit.get('owner'):raise UnsafeDeletion('Settlement and unit owner do not match')
        if unit.get('indianSettlement')!=allow_settlement and not any(x.get('id')==uid for x in owner.findall('ownedUnits')):raise UnsafeDeletion('Unit is not affiliated')
    else:
        loc=unit.get('location','')
        par=parent.get(unit)
        if unit.get('indianSettlement') or loc.startswith('indianSettlement:'):
            home=unit.get('indianSettlement')
            if not home:raise UnsafeDeletion('Native unit with no resolvable home settlement')
            return remove_unit(xml,uid,allow_settlement=home)
        
        if par is None or par.tag not in ('tile','colony','colonyTile','building'):
            raise UnsafeDeletion('Unsupported unit container: '+(par.tag if par is not None else '?'))
        if not (loc.startswith('tile:') or loc.startswith('colony:') or loc.startswith('colonyTile:') or loc.startswith('building:')):
            raise UnsafeDeletion('Unsupported unit location: '+loc)
        if unit.findall('unit') or unit.findall('goods') or unit.findall('goodsContainer'):
            raise UnsafeDeletion('Carrier with passengers/cargo')
        if any(c.get('location')==uid for c in root.iter('unit')):raise UnsafeDeletion('Unit is carrying another unit')
    known=set();unknown=[]
    for element in root.iter():
        for attr,value in element.attrib.items():
            if value!=uid:continue
            if element is unit and attr=='id':known.add('unit')
            elif element.tag=='aiUnit' and attr=='id':known.add('aiUnit')
            elif allow_settlement and element.tag=='ownedUnits' and attr=='id' and parent.get(element) is not None and parent[element].get('id')==allow_settlement:known.add('ownedUnits')
            else:unknown.append((element.tag,attr))
    if unknown:raise UnsafeDeletion('Unknown unit references: '+str(unknown[:10]))
    spans=[]
    for tag in sorted(known):
        found=_element_spans(xml,tag,uid)
        if len(found)!=1:raise UnsafeDeletion('Ambiguous '+tag+' definition for '+uid)
        spans.extend(found)
    new=_apply_spans(xml,spans)
    check=ET.fromstring(new)
    if any(uid in e.attrib.values() for e in check.iter()):raise UnsafeDeletion('Dangling unit reference')
    return new

def ancestors(element,parent):
    while element in parent:
        element=parent[element]
        yield element

def plan_settlement(xml,sid):
    if not re.fullmatch(r'indianSettlement:\d+',sid):raise UnsafeDeletion('Invalid settlement ID')
    root=ET.fromstring(xml);parent={c:p for p in root.iter() for c in p}
    real=[x for x in root.findall('./game/map/tile/indianSettlement') if x.get('id')==sid]
    if len(real)!=1:raise UnsafeDeletion('Authoritative settlement is not unique')
    s=real[0]
    ids={x.get('id') for x in s.findall('ownedUnits') if x.get('id')}
    ids.update(u.get('id') for u in root.iter('unit') if u.get('indianSettlement')==sid and u.get('id'))
    ids.update(u.get('id') for u in s.iter('unit') if u.get('id'))
    units=[u for u in root.iter('unit') if u.get('id') in ids]
    if len(units)!=len(ids):raise UnsafeDeletion('Missing or repeated owned unit definitions')
    if any(u.get('owner')!=s.get('owner') for u in units):raise UnsafeDeletion('Mixed owner units')
    # Some missions can target the settlement even when their AI unit belongs to another village.
    unexpected=[]
    for e in root.iter():
        for key,value in e.attrib.items():
            if value==sid and not ((e.tag=='indianSettlement' and key=='id') or (e.tag=='tile' and key=='owningSettlement') or (e.tag=='unit' and key in ('indianSettlement','location')) or (any(a.tag=='aiUnit' and a.get('id') in ids for a in ancestors(e,parent)))):
                unexpected.append((e.tag,key))
    if unexpected:raise UnsafeDeletion('External settlement dependency: '+str(unexpected[:8]))
    # Cached representations may contain other game objects: remove only cached settlement subtree.
    return {'name':s.get('name'),'id':sid,'owner':s.get('owner'),'units':sorted(ids), 'cached_copies':sum(1 for e in root.iter('indianSettlement') if e.get('id')==sid)-1,'claimed_tiles':sum(e.get('owningSettlement')==sid for e in root.iter('tile'))}

def remove_settlement(xml,sid):
    plan=plan_settlement(xml,sid)
    # Process units first, while valid village still exists.
    for uid in plan['units']:
        xml=remove_unit(xml,uid,allow_settlement=sid)
    root=ET.fromstring(xml)
    # Prevent deletion if any unexpected remaining references exist.
    for e in root.iter():
        for k,v in e.attrib.items():
            if v==sid and not ((e.tag=='indianSettlement' and k=='id') or (e.tag=='tile' and k=='owningSettlement')):
                raise UnsafeDeletion('Unexpected surviving relationship: '+e.tag+'.'+k)
    spans=_element_spans(xml,'indianSettlement',sid)
    if len(spans)!=1+plan['cached_copies']:
        raise UnsafeDeletion('Cached representations cannot be identified uniquely')
    # Reject overlapping cached/authoritative structures.
    xml=_apply_spans(xml,spans)
    # Clear ownership relationships; terrain itself is retained.
    pattern=rb'(?<![A-Za-z])owningSettlement="'+re.escape(sid.encode())+rb'"'
    xml,n=re.subn(pattern,b'',xml)
    if n!=plan['claimed_tiles']:raise UnsafeDeletion('Unexpected number of claimed tiles removed')
    final=ET.fromstring(xml)
    if any(sid in e.attrib.values() for e in final.iter()):raise UnsafeDeletion('Unresolved settlement reference')
    return xml
