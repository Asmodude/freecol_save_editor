"""Game-rules based unit-equipment validation. No warehouse inventory changes."""
from movement_rules import movement_cap, UnknownMovement
ROLES=('model.role.default','model.role.soldier','model.role.dragoon','model.role.scout','model.role.pioneer')

# Standard FreeCol non-personnel unit types are never eligible for equipment.
# This safety guard complements the saved ability flags, which may be incomplete
# or inherited; do not infer arbitrary new unit types are personnel.
_NON_EQUIPPABLE_TYPES = frozenset((
    'treasuretrain', 'wagontrain', 'artillery', 'damagedartillery',
    'caravel', 'merchantman', 'galleon', 'frigate', 'privateer',
    'manowar', 'kingmanowar', 'sloop',
))

def _is_non_equippable_type(unit_type):
    identifier = (unit_type.get('id') or '').rsplit('.', 1)[-1].lower()
    if identifier in _NON_EQUIPPABLE_TYPES:
        return True
    abilities = {a.get('id'): a.get('value', 'true') == 'true'
                 for a in unit_type.findall('ability')}
    return any(abilities.get(name, False) for name in (
        'model.ability.navalUnit', 'model.ability.carryTreasure',
        'model.ability.native'))


def validate_equipment(root,unit,role,count,*,rules=None):
    if role not in ROLES:raise ValueError('Unsupported equipment role')
    options=rules.roles.get(role, ()) if rules is not None else [r for r in root.iter('role') if r.get('id')==role]
    types=rules.types.get(unit.get('unitType'), ()) if rules is not None else [t for t in root.iter('unit-type') if t.get('id')==unit.get('unitType')]
    if len(options)!=1 or len(types)!=1:raise ValueError('Role or unit type not uniquely defined')
    config=options[0]; unit_type=types[0]
    maximum=int(config.get('maximum-count','1'))
    if role == 'model.role.default':
        if count != 0: raise ValueError('Default role must have zero equipment count')
    elif not 1<=count<=maximum:raise ValueError('Equipment count outside ruleset limit')
    # Evaluate explicit constraints declared by role against unit type abilities.
    def abilities(e):
        return {a.get('id'):a.get('value','true')=='true' for a in e.findall('ability')}
    active=abilities(unit_type)
    # Unit types can inherit properties in the specification; fail closed if uncertain.
    if role!='model.role.default':
        if _is_non_equippable_type(unit_type):
            raise ValueError('This unit type cannot be equipped')
        if active.get('model.ability.navalUnit',False):raise ValueError('Cannot equip naval units')
        if active.get('model.ability.native',False):raise ValueError('Native equipment is outside this release')
        if not active.get('model.ability.canBeEquipped',False):
            raise ValueError('Unit type does not explicitly support equipping')
    for requirement in config.findall('required-ability'):
        name=requirement.get('id'); expected=requirement.get('value','true')=='true'
        if active.get(name,False)!=expected:raise ValueError('Unit cannot use this role: '+name)
    test=type('U',(),{'get':lambda self,k,default=None: (role if k=='role' else unit.get(k,default))})()
    movement_cap(root,test,rules=rules)
    return True
