"""Qt-only human-friendly labels for FreeCol identifiers.

Never modify or reinterpret IDs, names or raw XML; this is display-only.
"""
import re
import presentation


def display_identifier(value):
    if value is None:
        return ''
    return presentation.readable(str(value))


def display_row(group, values):
    values=list(values)
    if group=='Units':
        values[1]=display_identifier(values[1])
        values[4]=display_identifier(values[4])
    if group=='Native settlements':
        # Columns: ID, Name, Owner, Location, Learnable skill, Wanted goods
        values[4]=display_identifier(values[4])
        values[5]=', '.join(display_identifier(part.strip())
                            for part in str(values[5] or '').split(',') if part.strip())
    return tuple(values)
