"""Read-only FreeCol Founding Father threshold from selected difficulty.

Never choose among conflicting difficulty presets by assuming a default.
"""
OPTION = 'model.option.foundingFatherFactor'


def next_founding_father_cost(player, document):
    root = getattr(document, 'root', None)
    if root is None:
        return None
    spec = next(root.iter('freecol-specification'), None)
    if spec is None:
        spec = next(root.iter('specification'), None)
    scope = spec if spec is not None else root
    selected = (spec.get('difficulty-level') or spec.get('difficultyLevel')) if spec is not None else None
    # For an actual saved game, use only the selected difficulty's subtree.
    # The specification includes all difficulty presets; querying all of
    # them as one collection incorrectly makes this option ambiguous.
    if selected:
        groups = [node for node in scope.iter('optionGroup')
                  if node.get('id') == selected]
        if len(groups) != 1:
            return None
        options = [node for node in groups[0].iter('integerOption')
                   if node.get('id') == OPTION]
    else:
        # Synthetic fixtures and minimal modded saves may embed a single
        # explicit option without a difficulty selector.
        options = [node for node in scope.iter('integerOption')
                   if node.get('id') == OPTION]
    values = {node.get('value') for node in options if node.get('value') is not None}
    if len(values) != 1:
        return None
    try:
        base = int(next(iter(values)))
    except ValueError:
        return None
    if base <= 0:
        return None
    fathers = player.find('foundingFathers')
    count = sum(1 for name in fathers.attrib
                if name.startswith('x') and name[1:].isdigit()) if fathers is not None else 0
    return base if count == 0 else 2 * (count + 1) * base + 1
