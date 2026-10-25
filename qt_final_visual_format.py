"""Presentation-only formatting for colony turns and saved map positions."""


def established_turn(value):
    """Never modify the underlying XML turn value."""
    return f'Turn {value}' if value is not None and str(value).strip() else ''


def colony_inspector_location(colony, document):
    """The same name as before, plus actual saved tile coordinates when available."""
    location = document.location_name(colony.get('tile'))
    xy = document.tiles.get(colony.get('tile'))
    if xy is None or len(xy) != 2 or any(v is None or v == '' for v in xy):
        return location
    coordinates = f'({xy[0]}, {xy[1]})'
    return f'{location} {coordinates}' if location else coordinates
