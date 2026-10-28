"""FreeCol national liberty eligibility from the saved player's nationType.

A colonial label alone is insufficient: unknownEnemy and REF cannot
recruit Founding Fathers. Fail closed when specification is unavailable.
"""
from xml.etree import ElementTree as ET

ABILITY = 'model.ability.electFoundingFather'


def can_edit_national_liberty(root, player):
    if player is None or player.get('playerType', '').lower() != 'colonial':
        return False
    if player.get('dead', '').lower() == 'true' or player.get('gold') == '-2147483648':
        return False
    nation_type = player.get('nationType')
    if not nation_type:
        return False
    types = {node.get('id'): node for node in root.iter()
             if node.tag in ('european-nation-type', 'indian-nation-type')
             and node.get('id')}
    visited = set()
    current = nation_type
    while current and current not in visited:
        visited.add(current)
        node = types.get(current)
        if node is None:
            return False
        for ability in node.findall('ability'):
            if ability.get('id') == ABILITY:
                return ability.get('value', 'true').lower() == 'true'
        current = node.get('extends')
    return False
