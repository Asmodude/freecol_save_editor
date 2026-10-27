"""Resolve tile locations to authoritative colony names for display only."""


def colony_tile_names(game):
    """Map tile IDs to colony names from actual map tiles, never cached copies."""
    result = {}
    for tile in game.findall("./map/tile"):
        tile_id = tile.get("id")
        colonies = [c for c in tile.findall("colony") if (c.get("id") or "").startswith("colony:")]
        if not tile_id or not colonies:
            continue
        if len(colonies) != 1 or tile_id in result:
            raise ValueError("Ambiguous colony on tile " + tile_id)
        result[tile_id] = colonies[0].get("name") or colonies[0].get("id")
    return result


def colony_building_names(game):
    """Map authoritative colony building IDs to colony names, excluding cached tiles."""
    result = {}
    for tile in game.findall('./map/tile'):
        for colony in tile.findall('colony'):
            colony_id = colony.get('id') or ''
            if not colony_id.startswith('colony:'):
                continue
            name = colony.get('name') or colony_id
            for element in colony.iter('building'):
                key = element.get('id')
                if key:
                    if key in result and result[key] != name:
                        raise ValueError('Ambiguous building location ' + key)
                    result[key] = name
    return result


def unit_locations(units):
    """Lookup only authoritative units; cached unit snapshots are excluded upstream."""
    return {u.get("id"): u for u in units if u.get("id")}


def location_label(key, locations, tiles, colony_tiles, units=None, _seen=None, buildings=None):
    if buildings and key in buildings:
        return buildings[key]
    if key in locations:
        return locations[key]
    if key in colony_tiles:
        return colony_tiles[key]
    if key in tiles:
        x, y = tiles[key]
        return f"Tile ({x},{y})"
    if key and key.startswith("unit:") and units and key in units:
        seen = set() if _seen is None else _seen
        if key in seen:
            return f"Aboard unit ({key}; cyclic location)"
        unit = units[key]
        unit_type = (unit.get("unitType") or "Unknown unit").removeprefix("model.unit.")
        next_key = unit.get("location")
        if next_key and next_key != key:
            where = location_label(next_key, locations, tiles, colony_tiles, units, seen | {key}, buildings)
            return f"Aboard {unit_type} ({where})"
        return f"Aboard {unit_type}"
    return key or ""
