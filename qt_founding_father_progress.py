"""Read-only threshold for the next FreeCol Founding Father.

FreeCol Player.getTotalFoundingFatherCost:
count == 0 ? base : 2 * (count + 1) * base + 1.
Do not invent a value if the effective option cannot be determined.
"""


def next_founding_father_cost(player, document):
    root = getattr(document, 'root', None)
    if root is None:
        return None
    options = [n for n in root.iter('integerOption')
               if n.get('id') == 'model.option.foundingFatherFactor']
    # The save's embedded ruleset may contain multiple difficulty presets.
    # Only use an unambiguous effective value; otherwise fail closed.
    values = {n.get('value') for n in options if n.get('value') is not None}
    if len(values) != 1:
        return None
    try:
        base = int(next(iter(values)))
    except ValueError:
        return None
    if base <= 0:
        return None
    fathers = player.find('foundingFathers')
    count = sum(1 for name in fathers.attrib if name.startswith('x') and name[1:].isdigit()) if fathers is not None else 0
    return base if count == 0 else 2 * (count + 1) * base + 1
