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


def location_label(key, locations, tiles, colony_tiles):
    if key in locations:
        return locations[key]
    if key in colony_tiles:
        return colony_tiles[key]
    if key in tiles:
        x, y = tiles[key]
        return f"Tile ({x},{y})"
    return key or ""
