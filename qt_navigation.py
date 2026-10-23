"""Pure Phase 1 player ownership filtering; never guess the human player."""
def human_player_id(document):
    candidates=[p.get('id') for p in document.players.values()
                if p.get('ai')=='false' and p.get('playerType')=='colonial']
    return candidates[0] if len(candidates)==1 else None


def rows_for_scope(document, group, scope):
    records=document.records.get(group,())
    own=human_player_id(document)
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
