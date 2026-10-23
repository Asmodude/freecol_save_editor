"""Pure contextual inspector formatting for Qt detail table selections.

A detail row is an already-rendered, read-only tuple. Never infer or change
underlying savegame relationships from its display values.
"""


def detail_inspection(section, headings, values):
    """Return (title, text) for a selected row in a contextual detail table."""
    fields = [(str(head), str(value)) for head, value in zip(headings, values)
              if value is not None and str(value) != '']
    label = next((value for head, value in fields
                  if head in ('Building', 'Unit type', 'Goods')), section)
    lines = [f'{section} — {label}', '']
    lines.extend(f'{head}: {value}' for head, value in fields)
    lines.extend(['', 'Read only · values shown as stored or resolved in the table'])
    return label, '\n'.join(lines)
