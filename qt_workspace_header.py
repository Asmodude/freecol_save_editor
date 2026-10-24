"""Pure display metadata for the Phase 1 graphical workspace header.

Use recorded nation identifiers and actual scoped records; never mock up counts
or infer attributes absent from the save.
"""
import presentation
from qt_navigation import human_player_id, rows_for_scope

TITLES = {
    'Players': 'Overview', 'Colonies': 'Colonies', 'Native settlements': 'Settlements',
    'Units': 'Units', 'National Goods': 'Goods', 'Founding Fathers': 'Founding Fathers',
    'Diplomacy': 'Diplomacy', 'Game properties': 'Game properties',
}


def workspace_identity(document, group, scope):
    """Return (title, subtitle, nation_id, is_native, filter_placeholder)."""
    label = TITLES.get(group, group)
    placeholder = 'Filter ' + label.lower() + '…'
    if document is None:
        return 'Savegame Explorer', 'Open a FreeCol save to begin', None, False, placeholder
    if group == 'Game properties':
        return label, 'Properties saved in this game', None, False, 'Filter properties…'
    pid = (human_player_id(document) if scope == 'mine' else
           scope[7:] if scope.startswith('player:') else
           scope[13:] if scope.startswith('native-owner:') else None)
    if group == 'Players' and scope == 'rivals':
        return 'Rival Nations', 'European colonial rivals in the save', None, False, 'Filter rivals…'
    if group == 'Native settlements' and scope == 'native':
        return 'Native Nations — Settlements', 'All saved native settlements', None, True, 'Filter settlements…'
    if scope.startswith('colony-id:'):
        element = next((c for c in document.colonies if c.get('id') == scope[10:]), None)
        if element is not None:
            pid = element.get('owner')
            label = element.get('name') or label
    elif scope.startswith('settlement-id:'):
        element = next((v for v in document.native_settlements if v.get('id') == scope[14:]), None)
        if element is not None:
            pid = element.get('owner')
            label = element.get('name') or label
    elif scope.startswith('unit-group|'):
        parts = scope.split('|')
        pid = parts[1] if len(parts) > 1 else None
    player = document.players.get(pid) if pid else None
    nation_id = (player.get('nationId') or player.get('nation')) if player is not None else None
    nation = presentation.readable(nation_id) if nation_id else ''
    native = player is not None and player.get('playerType') in ('indian', 'native')
    count = len(rows_for_scope(document, group, scope)) if group in ('Colonies','Units','Native settlements') else None
    if count is not None and not scope.startswith(('colony-id:', 'settlement-id:')):
        label = f'{label} ({count})'
    title = f'{nation} — {label}' if nation else label
    subtitle = (f'All {label.split(" (")[0].lower()} belonging to {nation}' if nation and
                not scope.startswith(('colony-id:', 'settlement-id:')) else
                f'Saved {group.lower()} information')
    return title, subtitle, nation_id, native, placeholder
