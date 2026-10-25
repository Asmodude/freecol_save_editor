"""Parse existing read-only Overview summaries into explicit display sections.

The source strings still come from qt_overview.record_overview; this module
only preserves their headings and associations for the graphical Qt view.
"""
SECTION_HEADINGS = (
    'Population and activity', 'Largest warehouse stockpiles',
    'Occupied buildings',
)


def overview_sections(text):
    """Return (record_title, [(section_title, [(label, value)], [notes])...]).

    Section headings belong to subsequent values, never to a detached notes
    area. The last guidance line stays separate from actual saved statistics.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return '', []
    sections = []
    heading = 'Colony properties'
    fields, notes = [], []

    def flush():
        if fields or notes:
            sections.append((heading, fields.copy(), notes.copy()))

    for line in lines[1:]:
        if line in SECTION_HEADINGS:
            flush()
            heading = line
            fields, notes = [], []
        elif ':' in line and not line.startswith('Select '):
            label, value = line.split(':', 1)
            if label.strip() and value.strip():
                fields.append((label.strip(), value.strip()))
            else:
                notes.append(line)
        else:
            notes.append(line)
    flush()
    return lines[0], sections
