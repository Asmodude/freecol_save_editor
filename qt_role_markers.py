"""Pure role-marker decisions for source versus pending unit equipment."""


def equipment_marker(source_role, has_staged_equipment):
    """Return 'staged', 'equipped', or None, based on session identity."""
    if has_staged_equipment:
        return 'staged'
    if source_role != 'model.role.default':
        return 'equipped'
    return None
