"""Identify authoritative unit XML records, excluding cached terrain copies.

FreeCol serializes missionary snapshots beneath <cachedTile>. These snapshots
are not additional live units and must never enter editable unit lists.
"""
from collections import Counter


def authoritative_units(game):
    parents = {child: parent for parent in game.iter() for child in parent}
    units = []
    for unit in game.iter("unit"):
        uid = unit.get("id", "")
        if not uid.startswith("unit:"):
            continue
        node = unit
        cached = False
        while node in parents:
            node = parents[node]
            if node.tag == "cachedTile":
                cached = True
                break
        if not cached:
            units.append(unit)
    identifiers = [u.get("id") for u in units]
    repeated = sorted(uid for uid, count in Counter(identifiers).items() if count != 1)
    if repeated:
        raise ValueError("Duplicate authoritative unit IDs: " + ", ".join(repeated[:8]))
    return units
