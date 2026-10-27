"""Conservative movement bounds read from FreeCol save's embedded Specification.
Movement values are FreeCol internal points (3 points usually equal one normal tile move).
Fail closed for rules we cannot evaluate, instead of inventing a maximum.
"""
import xml.etree.ElementTree as ET
from types import MappingProxyType

class UnknownMovement(ValueError): pass

class EquipmentRulesIndex:
    """Read-only lookups for one opened save; retain duplicate IDs for safe refusal."""

    def __init__(self, root):
        roles, types, players = {}, {}, {}
        for node in root.iter():
            key = node.get('id')
            if node.tag == 'role':
                roles.setdefault(key, []).append(node)
            elif node.tag == 'unit-type':
                types.setdefault(key, []).append(node)
            elif node.tag == 'player':
                players.setdefault(key, node)
        self.roles = MappingProxyType({key: tuple(value) for key, value in roles.items()})
        self.types = MappingProxyType({key: tuple(value) for key, value in types.items()})
        self.players = MappingProxyType(players)


def movement_cap(root, unit, *, rules=None):
    uid=unit.get('unitType'); role=unit.get('role','model.role.default')
    types=rules.types.get(uid, ()) if rules is not None else [e for e in root.iter('unit-type') if e.get('id')==uid]
    roles=rules.roles.get(role, ()) if rules is not None else [e for e in root.iter('role') if e.get('id')==role]
    if len(types)!=1 or len(roles)!=1:raise UnknownMovement('Unit type or role not defined uniquely by saved ruleset')
    ut=types[0];r=roles[0]
    try: base=int(ut.get('movement'))
    except (TypeError,ValueError):raise UnknownMovement('No unit movement value in the ruleset')
    result=base
    for source in (ut,r):
        for mod in source.findall('modifier'):
            if mod.get('id')=='model.modifier.movementBonus':
                if mod.get('type')!='additive':raise UnknownMovement('Non-additive movement modifier unsupported')
                try:result+=int(float(mod.get('value')))
                except (ValueError,KeyError):raise UnknownMovement('Invalid movement modifier')
    # Some unit owners, nations, founding fathers, or cargo conditions may modify
    # ship movement. Do not invent a ship ceiling from base movement.
    if any(a.get('id')=='model.ability.navalUnit' and a.get('value')=='true' for a in ut.findall('ability')):
        raise UnknownMovement('Naval movement may depend on cargo or other dynamic modifiers; not editable in this test release')
    # Examine relevant owner modifiers: explicit movement bonuses at player level.
    player=(rules.players.get(unit.get('owner')) if rules is not None
            else next((v for v in root.iter('player') if v.get('id')==unit.get('owner')),None))
    if player is None: raise UnknownMovement('Missing unit owner')
    if any(m.get('id')=='model.modifier.movementBonus' for m in player.iter('modifier')):
        raise UnknownMovement('Unit owner has movement modifiers not yet evaluated')
    if result<0 or result>100:raise UnknownMovement('Movement maximum out of supported range')
    return result
