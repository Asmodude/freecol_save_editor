"""Pure Phase 1 player ownership filtering; never guess the human player."""
from qt_founding_fathers import father_rows
from qt_national_goods import national_goods
from qt_unit_groups import scoped_units
from qt_diplomacy import diplomacy_rows
def human_player_id(document):
    candidates=[p.get('id') for p in document.players.values()
                if p.get('ai')=='false' and p.get('playerType')=='colonial']
    return candidates[0] if len(candidates)==1 else None


def rows_for_scope(document, group, scope):
    if group == 'Units' and scope.startswith('unit-group|'):
        return scoped_units(document,scope)
    if group == 'Diplomacy':
        own = human_player_id(document)
        pid = own if scope == 'mine' else scope[len('player:'):] if scope.startswith('player:') else None
        return diplomacy_rows(document,pid)
    if group == 'National Goods':
        own = human_player_id(document)
        pid = own if scope == 'mine' else scope[len('player:'):] if scope.startswith('player:') else None
        return national_goods(document,pid)
    if group == 'Founding Fathers':
        own = human_player_id(document)
        pid = own if scope == 'mine' else scope[len('player:'):] if scope.startswith('player:') else None
        player = document.players.get(pid) if pid else None
        return father_rows(player) if player is not None else []
    records=document.records.get(group,())
    own=human_player_id(document)
    if scope.startswith('settlement-id:') and group=='Native settlements':
        target=scope[len('settlement-id:'):]
        return [e for e in records if e.get('id')==target]
    if scope.startswith('colony-id:') and group=='Colonies':
        target=scope[len('colony-id:'):]
        return [e for e in records if e.get('id')==target]
    if scope.startswith('player:'):
        target=scope[len('player:'):]
        return [e for e in records if (e.get('id') if group=='Players' else e.get('owner'))==target]
    if scope.startswith('native-owner:') and group=='Native settlements':
        target=scope[len('native-owner:'):]
        return [e for e in records if e.get('owner')==target]
    if scope=='all':
        return list(records)
    if scope=='mine':
        if own is None:
            return []
        return [e for e in records if (e.get('id') if group=='Players' else e.get('owner'))==own]
    if scope=='rivals':
        return [e for e in records if e.get('playerType')=='colonial' and e.get('id')!=own] if group=='Players' else []
    if scope=='native':
        return list(records) if group=='Native settlements' else []
    return []
