"""FreeCol v0.4.2 conservative XML attribute edits and archive validation."""
import os, copy, re, tempfile, zipfile, shutil
from pathlib import Path
from deletion_engine import remove_unit, remove_settlement
from movement_rules import movement_cap, UnknownMovement
import xml.etree.ElementTree as ET

def real_settlements(root):
    game=root.find('game')
    return game.findall('./map/tile/indianSettlement') if game is not None else []

# UI stages tuples (old, new) using keys (object-id, field-id).
# A field-id can be model.goods.foo, gold, tax or experience.
LIMIT=2_147_483_647
COLONY_RE=re.compile(rb'<colony\b[^>]*\bid="(colony:\d+)"[^>]*>',re.S)
GOODS_RE=re.compile(rb'<goods\b[^>]*\btype="(model\.goods\.[^"]+)"[^>]*\bamount="(\d+)"[^>]*>',re.S)

def _replace_span(data, start, end, old, new):
    if int(data[start:end]) != old: raise ValueError(f'Stale value: expected {old}, found {data[start:end]!r}')
    return data[:start]+str(new).encode('ascii')+data[end:]

def _find_tag(data, object_id):
    tag=object_id.split(':',1)[0]
    if tag not in ('player','unit'):raise ValueError('Unsupported object type')
    pattern=rb'<'+tag.encode()+rb'\b[^>]*\bid="'+re.escape(object_id.encode())+rb'"[^>]*>'
    matches=list(re.finditer(pattern,data,re.S))
    if len(matches)!=1: raise ValueError(f'Expected exactly one {object_id}; found {len(matches)}')
    return matches[0]


# The local Sons of Liberty editor does not award any Founding Father progress.
# The stored whole percentage is derived from colony accumulated liberty and
# the current population. Currently no special SoL modifier is supported.
def colony_sol_values(old_attrs, population, target):
    if not isinstance(target,int) or not 0 <= target <= 100:
        raise ValueError('Sons of Liberty must be 0–100%')
    if population <= 0: raise ValueError('Cannot edit an empty colony')
    old_liberty = int(old_attrs['liberty'])
    current = int(old_attrs['sonsOfLiberty'])
    # Fail closed if colony percentages are not explained by normal FreeCol math.
    expected = min(100, old_liberty * 100 // (population * 200))
    if current != expected:
        raise ValueError(f'Colony SoL has additional modifiers or an unexpected formula ({current}% vs {expected}%); refusing unsafe edit')
    if target == current: return None
    # Choose minimal points yielding the desired truncated whole percentage.
    new_liberty = (target * population * 200 + 99) // 100
    rebels = population * target // 100
    tories = population - rebels
    bonus = min(2, target // 50)
    return {'liberty':new_liberty,'sonsOfLiberty':target,'oldSonsOfLiberty':target,
            'tories':tories,'oldTories':tories,'productionBonus':bonus}

def change_colony_sol(xml,object_id,old,new):
    matches=[m for m in COLONY_RE.finditer(xml) if m.group(1)==object_id.encode()]
    if len(matches)!=1:raise ValueError('Colony not uniquely found')
    match=matches[0]
    tag=match.group(0)
    attrs={k.decode():v.decode() for k,v in re.findall(rb'([A-Za-z]+)="([^"]*)"',tag)}
    if int(attrs['sonsOfLiberty']) != old:raise ValueError('Stale colony SoL percentage')
    # Resolve population from the parsed game object to avoid counting workers
    # incorrectly by guessing based on textual XML nesting.
    root=ET.fromstring(xml)
    colony=next((c for c in root.iter('colony') if c.get('id')==object_id),None)
    if colony is None:raise ValueError('Colony not found')
    population=sum(1 for u in colony.iter('unit') if u.get('id'))
    updates=colony_sol_values(attrs,population,new)
    if updates is None:return xml
    for field,value in updates.items():
        pattern=rb'(?<![\w:-])'+field.encode()+rb'="(\d+)"'
        hits=list(re.finditer(pattern,tag))
        if len(hits)!=1:raise ValueError(f'Missing/duplicate colony attribute {field}')
        h=hits[0]
        tag=tag[:h.start(1)]+str(value).encode()+tag[h.end(1):]
    return xml[:match.start()]+tag+xml[match.end():]

def change_native_field(xml,object_id,field,old,new):
    # Edit one specific relationship only; preserve all unrelated bytes.
    root=ET.fromstring(xml)
    if field=='learnableSkill':
        matches=[e for e in real_settlements(root) if e.get('id')==object_id]
        if len(matches)!=1:raise ValueError('Unknown settlement')
        known={e.get('learnableSkill') for e in real_settlements(root) if e.get('learnableSkill')}
        if new not in known:raise ValueError('Unrecognised teaching skill')
        tag=b'indianSettlement'; pattern=rb'<indianSettlement\b[^>]*\bid="'+re.escape(object_id.encode())+rb'"[^>]*>'
        hits=list(re.finditer(pattern,xml,re.S))
        hits=[h for h in hits if b'lastTribute=' in h.group(0) and b'convertProgress=' in h.group(0)]
        if len(hits)!=1:raise ValueError('Authoritative settlement tag not unique')
        m=hits[0];chunk=m.group(0)
        attr=re.search(rb'\blearnableSkill="([^"]+)"',chunk)
        if attr is None or attr.group(1).decode()!=old:raise ValueError('Teaching skill has changed')
        a=m.start()+attr.start(1);b=m.start()+attr.end(1)
        return xml[:a]+new.encode('ascii')+xml[b:]
    if '|' not in field:raise ValueError('Unsupported relationship field')
    kind,other=field.split('|',1)
    if kind not in ('stance','tension','alarm') or not re.fullmatch(r'player:\d+',other):raise ValueError('Invalid relationship')
    owner_tag='indianSettlement' if kind=='alarm' else 'player'
    if not object_id.startswith('indianSettlement:' if kind=='alarm' else 'player:'):raise ValueError('Wrong owner type')
    owner=next((e for e in (real_settlements(root) if kind=='alarm' else root.iter(owner_tag)) if e.get('id')==object_id),None)
    if owner is None:raise ValueError('Missing owner')
    if other==object_id:raise ValueError('Cannot relate player to itself')
    if not any(e.get('id')==other for e in root.iter('player')):raise ValueError('Unknown target player')
    if kind=='stance' and new not in ('peace','war','cease_fire','alliance'):raise ValueError('Unknown stance')
    if kind!='stance' and (not isinstance(new,int) or new<0 or new>2147483647):raise ValueError('Invalid numeric relationship')
    if kind=='stance':
        reverse=next((e for e in root.iter('player') if e.get('id')==other),None)
        reciprocal=next((e for e in reverse.findall('stance') if e.get('player')==object_id),None)
        if reciprocal is None:raise ValueError('Reciprocal stance missing; refuse unsafe change')
        if old != reciprocal.get('value'):raise ValueError('Asymmetric existing stance; refuse unsafe change')
    # Distinguish a missing alarm record from a value of zero.
    existing=[e for e in owner.findall(kind) if e.get('player')==other]
    if len(existing)>1:raise ValueError('Duplicate relation entries')
    if existing and str(old)!=existing[0].get('value'):raise ValueError('Stale relation')
    if not existing:raise ValueError('Cannot add a missing relationship in this safety release')
    start_pat=rb'<'+owner_tag.encode()+rb'\b[^>]*\bid="'+re.escape(object_id.encode())+rb'"[^>]*>'
    starts=list(re.finditer(start_pat,xml,re.S))
    if kind=='alarm':
        starts=[m for m in starts if b'lastTribute=' in m.group(0) and b'convertProgress=' in m.group(0)]
    if len(starts)!=1:raise ValueError('Authoritative owner not unique')
    start=starts[0];end=xml.find(b'</'+owner_tag.encode()+b'>',start.end())
    if end<0:raise ValueError('Unclosed owner')
    inside=xml[start.end():end]
    entry_pat=rb'<'+kind.encode()+rb'\b[^>]*\bplayer="'+re.escape(other.encode())+rb'"[^>]*>'
    matches=list(re.finditer(entry_pat,inside,re.S))
    if existing:
        if len(matches)!=1:raise ValueError('Relationship XML not unique')
        mm=matches[0]; val=re.search(rb'\bvalue="([^"]+)"',mm.group())
        if val is None or val.group(1).decode()!=str(old):raise ValueError('Stale relation value')
        a=start.end()+mm.start()+val.start(1);b=start.end()+mm.start()+val.end(1)
        xml=xml[:a]+str(new).encode()+xml[b:]
    else:
        if matches:raise ValueError('Unexpected relation')
        # Create a new local alarm element, never modify national tension.
        xml=xml[:end]+b'<alarm player="'+other.encode()+b'" value="'+str(new).encode()+b'"></alarm>'+xml[end:]
    if kind=='stance':
        xml=_change_reciprocal_stance(xml,other,object_id,old,new)
    return xml

def _change_reciprocal_stance(xml,owner_id,target_id,old,new):
    start_pat=rb'<player\b[^>]*\bid="'+re.escape(owner_id.encode())+rb'"[^>]*>'
    matches=list(re.finditer(start_pat,xml,re.S))
    if len(matches)!=1:raise ValueError('Reciprocal player not unique')
    m=matches[0];end=xml.find(b'</player>',m.end())
    inside=xml[m.end():end]
    st=rb'<stance\b[^>]*\bplayer="'+re.escape(target_id.encode())+rb'"[^>]*>'
    matches=list(re.finditer(st,inside,re.S))
    if len(matches)!=1:raise ValueError('Reciprocal stance missing')
    x=matches[0];value=re.search(rb'\bvalue="([^"]+)"',x.group())
    if value is None or value.group(1).decode()!=str(old):raise ValueError('Reciprocal changed')
    a=m.end()+x.start()+value.start(1);b=m.end()+x.start()+value.end(1)
    return xml[:a]+new.encode()+xml[b:]

def proportional_movement(moves, old_cap, new_cap):
    """Map remaining moves proportionally, rounding half up (not Python bankers' rounding)."""
    if old_cap <= 0 or new_cap < 0 or not 0 <= moves <= old_cap:
        raise ValueError('Invalid source movement for role conversion')
    return min(new_cap, (2 * moves * new_cap + old_cap) // (2 * old_cap))


def _equipment_movement_old(root, unit_id, equipment):
    """Movement that equipment staging will produce before any explicit movesLeft edit."""
    unit = next((u for u in root.iter('unit') if u.get('id') == unit_id), None)
    if unit is None:
        raise ValueError('Unit not found for movement recalculation')
    old_cap = movement_cap(root, unit)
    new_unit = ET.Element('unit', dict(unit.attrib, role=equipment[1][0],
                                      roleCount=str(equipment[1][1])))
    new_cap = movement_cap(root, new_unit)
    return proportional_movement(int(unit.get('movesLeft', '0')), old_cap, new_cap)


def ordered_edits_for_application(original, edits):
    """Keep the source-original session schema while applying dependent moves after role."""
    root = ET.fromstring(original)
    def order(item):
        key = item[0]
        return (0 if key[1] in ('deleteUnit', 'deleteNativeUnit') else
                1 if key[1] == 'deleteSettlement' else
                2 if key[1] == 'equipment' else
                3 if key[1] == 'movesLeft' else 4, key)
    result = []
    for key, (old, new) in sorted(edits.items(), key=order):
        if key[1] == 'movesLeft' and (key[0], 'equipment') in edits:
            expected_source = next((u for u in root.iter('unit') if u.get('id') == key[0]), None)
            if expected_source is None or int(expected_source.get('movesLeft', '-1')) != old:
                raise ValueError('Movement source mismatch')
            old = _equipment_movement_old(root, key[0], edits[(key[0], 'equipment')])
        result.append((key, (old, new)))
    return result


def change_equipment(xml, object_id, old, new):
    """Replace role and roleCount in one XML start tag, preserving unit type and other bytes."""
    root=ET.fromstring(xml)
    units=[u for u in root.iter('unit') if u.get('id')==object_id]
    if len(units)!=1:raise ValueError('Unit is not unique')
    unit=units[0]
    old_role,old_count=old
    new_role,new_count=new
    if new_role == 'model.role.default': new_count = 0
    if (unit.get('role','model.role.default'),int(unit.get('roleCount','1')))!=(old_role,old_count):
        raise ValueError('Stale equipment data')
    from equipment_rules import validate_equipment
    validate_equipment(root,unit,new_role,new_count)
    check=ET.Element('unit',dict(unit.attrib,role=new_role,roleCount=str(new_count)))
    try: cap=movement_cap(root,check)
    except UnknownMovement as exc:raise ValueError('Unable to verify movement after equipping: '+str(exc))
    # Convert remaining movement proportionally between role caps (half-up rounding).
    original_moves=int(unit.get('movesLeft','0'))
    original_cap=movement_cap(root,unit)
    effective_moves=proportional_movement(original_moves,original_cap,cap)
    tag=_find_tag(xml,object_id)
    text=tag.group(0)
    for name,value in (('role',new_role),('roleCount',str(new_count)),('movesLeft',str(effective_moves))):
        match=re.search(rb'(?<![\w:-])'+name.encode()+rb'="([^"]*)"',text)
        if not match:raise ValueError('Missing '+name+' on unit')
        text=text[:match.start(1)]+value.encode()+text[match.end(1):]
    return xml[:tag.start()]+text+xml[tag.end():]

def change_field(xml, object_id, field, old, new):
    if field=='equipment':return change_equipment(xml,object_id,old,new)
    if field=="deleteUnit":
        if old!="present" or new!="delete":raise ValueError("Invalid deletion request")
        return remove_unit(xml,object_id)
    if field=="deleteSettlement":
        if old!="present" or new!="delete":raise ValueError("Invalid deletion request")
        return remove_settlement(xml,object_id)
    if field=="deleteNativeUnit":
        if old != "present" or new != "delete":raise ValueError('Invalid deletion request')
        return _remove_native_unit(xml,object_id.split('|',1)[0],object_id.split('|',1)[1])
    if field=="learnableSkill" or "|" in field:
        return change_native_field(xml,object_id,field,old,new)
    if field=='movesLeft':
        if not object_id.startswith('unit:'):raise ValueError('Movement edit requires unit ID')
        root=ET.fromstring(xml)
        units=[u for u in root.iter('unit') if u.get('id')==object_id]
        if len(units)!=1:raise ValueError('Unit not unique')
        cap=movement_cap(root,units[0])
        if not isinstance(new,int) or not 0<=new<=cap:raise ValueError(f'Movement allowed range: 0–{cap} for {object_id}')
        match=_find_tag(xml,object_id)
        hit=re.search(rb'(?<![\w:-])movesLeft="(\d+)"',match.group(0))
        if hit is None:raise ValueError('Missing movement value')
        return _replace_span(xml,match.start()+hit.start(1),match.start()+hit.end(1),old,new)
    if field == "sonsOfLibertyTarget":
        if not object_id.startswith("colony:"):raise ValueError("SoL target must belong to a colony")
        return change_colony_sol(xml,object_id,old,new)
    if not isinstance(new,int) or not 0 <= new <= (100 if field=='tax' else 200 if field=='experience' else LIMIT):
        raise ValueError(f'{field}: out of range')
    if field.startswith('model.goods.'):
        if not object_id.startswith('colony:'):raise ValueError('Invalid goods owner')
        matches=[m for m in COLONY_RE.finditer(xml) if m.group(1)==object_id.encode()]
        if len(matches)!=1:raise ValueError('Colony not uniquely found')
        a=matches[0].start();b=xml.find(b'</colony>',matches[0].end())
        if b<0:raise ValueError('Missing colony closing tag')
        seg=xml[a:b]
        store=re.search(rb'<storedGoods\b[^>]*>(.*?)</storedGoods>',seg,re.S)
        if not store:raise ValueError('No stored goods element')
        found=[m for m in GOODS_RE.finditer(store.group(1)) if m.group(1)==field.encode()]
        if len(found)>1:raise ValueError('Duplicated goods record')
        if not found:
            if old!=0:raise ValueError('Cannot create stock with a nonzero original amount')
            if new==0:return xml
            # Restrict insertion to the known game's types and a well-formed storedGoods node.
            insert_at=a+store.end(1)
            element=b'<goods type="'+field.encode('ascii')+b'" amount="'+str(new).encode('ascii')+b'"></goods>'
            return xml[:insert_at]+element+xml[insert_at:]
        m=found[0]
        s=a+store.start(1)+m.start(2); e=a+store.start(1)+m.end(2)
        return _replace_span(xml,s,e,old,new)
    if field == 'liberty':
        # National liberty is player progress, not goods or colony SoL.
        if not object_id.startswith('player:'):
            raise ValueError('National liberty requires a player ID')
        candidates=[p for p in ET.fromstring(xml).iter('player')
                    if p.get('id')==object_id]
        if len(candidates)!=1 or candidates[0].get('playerType')!='colonial':
            raise ValueError('National liberty requires a unique colonial player')
    allowed={'player:':('gold','tax','liberty'),'unit:':('experience',)}
    if not any(object_id.startswith(prefix) and field in fields for prefix,fields in allowed.items()):
        raise ValueError(f'Unsupported edit: {object_id}.{field}')
    match=_find_tag(xml,object_id)
    attr=re.search(rb'(?<![\w:-])'+re.escape(field.encode())+rb'="(\d+)"',match.group(0))
    if not attr:raise ValueError(f'{field} attribute missing or not a nonnegative integer')
    return _replace_span(xml,match.start()+attr.start(1),match.start()+attr.end(1),old,new)


def _remove_native_unit(xml, unit_id, settlement_id):
    """Conservative native-unit deletion: refuses unforeseen external references."""
    if not re.fullmatch(r'unit:\d+', unit_id) or not re.fullmatch(r'indianSettlement:\d+', settlement_id):
        raise ValueError('Invalid unit or native settlement ID')
    root=ET.fromstring(xml)
    settlements=real_settlements(root)
    settlements=[s for s in settlements if s.get('id')==settlement_id]
    if len(settlements)!=1: raise ValueError('Home settlement is not unique')
    village=settlements[0]
    owned=[e for e in village.findall('ownedUnits') if e.get('id')==unit_id]
    units=[u for u in root.iter('unit') if u.get('id')==unit_id]
    if len(units)!=1:raise ValueError('Unit record is not unique')
    unit=units[0]
    if unit.get('owner')!=village.get('owner'):raise ValueError('Unit owner differs from native nation')
    if unit.get('indianSettlement')!=settlement_id and not owned:
        raise ValueError('Unit is not affiliated with the selected settlement')
    # All references: definition, AI-controller, owning-settlement reference.
    parents={child:parent for parent in root.iter() for child in parent}
    known=[];unknown=[]
    for e in root.iter():
        for key,val in e.attrib.items():
            if val!=unit_id:continue
            if e is unit and key=='id':known.append(('unit',e))
            elif e.tag=='ownedUnits' and key=='id' and parents.get(e) is village: known.append(('ownedUnits',e))
            elif e.tag=='aiUnit' and key=='id':known.append(('aiUnit',e))
            else:unknown.append((e.tag,key))
    if unknown:raise ValueError('Unsafe external references: '+str(unknown[:8]))
    if not any(kind=='unit' for kind,_ in known):raise ValueError('Missing authoritative unit')
    spans=[]
    for kind,e in known:
        pattern=rb'<'+kind.encode()+rb'\b[^>]*\bid="'+re.escape(unit_id.encode())+rb'"[^>]*>'
        hits=list(re.finditer(pattern,xml,re.S))
        if len(hits)!=1:raise ValueError(f'{kind} XML record not unique')
        m=hits[0]
        # These three node types cannot nest another element of the same type.
        end=xml.find(b'</'+kind.encode()+b'>',m.end())
        if end<0:raise ValueError('Unclosed '+kind)
        spans.append((m.start(),end+len(kind)+3))
    for start,end in sorted(spans,reverse=True):xml=xml[:start]+xml[end:]
    after=ET.fromstring(xml)
    if any(e.get('id')==unit_id for e in after.iter('unit')):raise ValueError('Unit deletion verification failed')
    if any(e.get('id')==unit_id for e in after.iter('aiUnit')):raise ValueError('AI deletion verification failed')
    if any(e.get('id')==unit_id for e in after.iter('ownedUnits')):raise ValueError('Settlement reference deletion verification failed')
    if any(unit_id in e.attrib.values() for e in after.iter()):raise ValueError('Dangling unit reference')
    return xml

def produce(src,dst,edits):
    src,dst=Path(src),Path(dst)
    if src.resolve()==dst.resolve():raise ValueError('Cannot overwrite the source')
    if dst.exists():raise FileExistsError(dst)
    if not edits:raise ValueError('No edits')
    with zipfile.ZipFile(src,'r') as zin:
        if zin.testzip() is not None:raise ValueError('Damaged source archive')
        infos=zin.infolist()
        if [i.filename for i in infos].count('savegame.xml')!=1:raise ValueError('Expected one savegame.xml')
        original=zin.read('savegame.xml')
        source_root=ET.fromstring(original)
        valid_goods={e.get('id') for e in source_root.iter('goods-type') if e.get('id')}
        valid_goods.update(e.get('type') for e in source_root.iter('goods') if e.get('type'))
        for (_,field),(_,new) in edits.items():
            if field.startswith('model.goods.') and field not in valid_goods:
                raise ValueError(f'Unknown goods type: {field}')
        # Reject requests to edit the same diplomatic relationship from both sides
        # in one batch: each stance edit already updates its reciprocal record.
        stance_edits={(obj,field.split('|',1)[1]) for (obj,field) in edits if field.startswith('stance|')}
        if any((other,obj) in stance_edits for obj,other in stance_edits):
            raise ValueError('Duplicate reciprocal stance changes staged. Edit the relationship from one player only.')
        xml=original
        deletion_keys={key for key in edits if key[1] in ('deleteUnit','deleteNativeUnit','deleteSettlement')}
        for key in deletion_keys:
            if key[1]=='deleteSettlement':
                sid=key[0]
                if any(k!=key and k[0]==sid for k in edits):raise ValueError('Do not mix settlement deletion with settlement property edits')
            if key[1]=='deleteUnit' and any(k!=key and k[0]==key[0] for k in edits):raise ValueError('Do not edit and delete the same unit')
        for (obj,field),(old,new) in ordered_edits_for_application(original, edits):
            xml=change_field(xml,obj,field,old,new)
        root=ET.fromstring(xml)
        for (obj,field),(_,new) in edits.items():
            if field.startswith('model.goods.'):
                owners=[c for c in root.iter('colony') if c.get('id')==obj]
                values=[g.get('amount') for c in owners for g in c.findall('./goodsContainer/storedGoods/goods') if g.get('type')==field]
            elif field=='sonsOfLibertyTarget':
                owners=[c for c in root.iter('colony') if c.get('id')==obj]
                values=[c.get('sonsOfLiberty') for c in owners]
            elif field in ('deleteUnit','deleteNativeUnit'):
                unit_id=obj.split('|',1)[0]
                values=[] if not any(e.get('id')==unit_id for e in root.iter('unit')) else ['still present']
            elif field=='deleteSettlement':
                values=[] if not any(e.get('id')==obj for e in root.iter('indianSettlement')) else ['still present']
            elif field=='equipment':
                values=[(u.get('role','model.role.default'),int(u.get('roleCount','1'))) for u in root.iter('unit') if u.get('id')==obj]
            elif field=='learnableSkill':
                values=[e.get(field) for e in real_settlements(root) if e.get('id')==obj]
            elif '|' in field:
                kind,other=field.split('|',1)
                tag='indianSettlement' if kind=='alarm' else 'player'
                values=[c.get('value') for e in (real_settlements(root) if kind=='alarm' else root.iter(tag)) if e.get('id')==obj for c in e.findall(kind) if c.get('player')==other]
            else:
                tag=obj.split(':',1)[0]
                values=[e.get(field) for e in root.iter(tag) if e.get('id')==obj]
            if values != ([] if field in ('deleteNativeUnit','deleteUnit','deleteSettlement') else [new] if field=='equipment' else [str(new)]):raise ValueError(f'Post-save validation failure: {obj}.{field}: {values}')
        fd,tmp=tempfile.mkstemp(prefix='.freecol_pending_',suffix='.fsg',dir=dst.parent)
        os.close(fd)
        try:
            with zipfile.ZipFile(tmp,'w') as zout:
                for info in infos:zout.writestr(copy.copy(info),xml if info.filename=='savegame.xml' else zin.read(info.filename))
            with zipfile.ZipFile(tmp) as check:
                if check.testzip() is not None or check.read('savegame.xml')!=xml:raise ValueError('Archive verification failed')
                for info in infos:
                    if info.filename!='savegame.xml' and check.read(info.filename)!=zin.read(info.filename):raise ValueError('Unexpected other archive member change')
            with open(dst,'xb') as out,open(tmp,'rb') as inp:shutil.copyfileobj(inp,out)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
    return {'changes':len(edits),'output':str(dst),'size_before':len(original),'size_after':len(xml)}
