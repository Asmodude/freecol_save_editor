"""Side-effect-free preflight of staged FreeCol edits.

Uses the same change_field ordering and key constraints as edit_backend.produce.
No save file is written and SaveDocument.xml_bytes is not mutated.
"""
import xml.etree.ElementTree as ET

from edit_backend import change_field, ordered_edits_for_application


def preflight(xml_bytes, edits):
    """Return the predicted XML bytes or raise the backend validation error."""
    root = ET.fromstring(xml_bytes)
    known_goods = {g.get('id') for g in root.iter('goods-type') if g.get('id')}
    known_goods.update(g.get('type') for g in root.iter('goods') if g.get('type'))
    for (_, field), _ in edits.items():
        if field.startswith('model.goods.') and field not in known_goods:
            raise ValueError(f'Unknown goods type: {field}')
    stances = {(obj, field.split('|', 1)[1])
               for obj, field in edits if field.startswith('stance|')}
    if any((other, obj) in stances for obj, other in stances):
        raise ValueError('Duplicate reciprocal stance changes staged. Edit the relationship from one player only.')
    for key in edits:
        obj, field = key
        if field == 'deleteSettlement' and any(k != key and k[0] == obj for k in edits):
            raise ValueError('Do not mix settlement deletion with settlement property edits')
        if field == 'deleteUnit' and any(k != key and k[0] == obj for k in edits):
            raise ValueError('Do not edit and delete the same unit')
    xml = xml_bytes
    for (obj, field), (old, new) in ordered_edits_for_application(xml_bytes, edits):
        xml = change_field(xml, obj, field, old, new)
    ET.fromstring(xml)
    return xml


def stage_checked(session, xml_bytes, key, original, new):
    """Preflight the proposed complete state before committing an edit.

    An explicit movement override equal to the source value is still meaningful
    when equipment staging has changed the *effective* movement.  For example,
    a colonist's source movesLeft=3, equipping as Dragoon projects 12, and
    manually requesting 3 must create a (3, 3) dependent edit, not vanish.
    """
    proposed = dict(session.edits)
    if key in proposed and proposed[key][0] != original:
        raise ValueError('Original value differs from opened save')
    equipment_key = (key[0], 'equipment')
    if key[1] == 'movesLeft' and equipment_key in proposed:
        from edit_backend import _equipment_movement_old
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_bytes)
        equipment_moves = _equipment_movement_old(root, key[0], proposed[equipment_key])
        if new == equipment_moves:
            proposed.pop(key, None)
        else:
            proposed[key] = (original, new)
    elif new == original:
        proposed.pop(key, None)
    else:
        proposed[key] = (original, new)
    preflight(xml_bytes, proposed)
    session.edits.clear()
    session.edits.update(proposed)
    return new


def unstage_checked(session, xml_bytes, key):
    """Prevent undo leaving mutually dependent edits unexportable."""
    proposed = dict(session.edits)
    proposed.pop(key, None)
    preflight(xml_bytes, proposed)
    session.unstage(key)
