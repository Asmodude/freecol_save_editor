"""Game-rules based unit-equipment validation. No warehouse inventory changes."""
from movement_rules import movement_cap, UnknownMovement
ROLES=('model.role.default','model.role.soldier','model.role.dragoon','model.role.scout','model.role.pioneer')

def validate_equipment(root,unit,role,count):
    if role not in ROLES:raise ValueError('Unsupported equipment role')
    options=[r for r in root.iter('role') if r.get('id')==role]
    types=[t for t in root.iter('unit-type') if t.get('id')==unit.get('unitType')]
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
        if active.get('model.ability.navalUnit',False):raise ValueError('Cannot equip naval units')
        if active.get('model.ability.native',False):raise ValueError('Native equipment is outside this release')
        if not active.get('model.ability.canBeEquipped',False):
            raise ValueError('Unit type does not explicitly support equipping')
    for requirement in config.findall('required-ability'):
        name=requirement.get('id'); expected=requirement.get('value','true')=='true'
        if active.get(name,False)!=expected:raise ValueError('Unit cannot use this role: '+name)
    test=type('U',(),{'get':lambda self,k,default=None: (role if k=='role' else unit.get(k,default))})()
    movement_cap(root,test)
    return True
