"""Sorting helpers for read-only FreeCol Qt tables.

Keep identifiers textual (unit:9 must not be sorted as quantity 9).
Only columns explicitly designated numerical use integer comparison.
"""
NUMERIC_COLUMNS = {
    'Players': {'Colonies','Settlements','Gold','Tax','Score'},
    'Colonies': {'Established','Liberty','Sons of Liberty','Production bonus'},
    'Units': {'Experience','Moves left','Max moves','Hit points'},
    'Native settlements': set(),
    'Founding Fathers': set(),
}
NUMERIC_DETAIL_COLUMNS = {'Workers','Tier','Experience','Amount'}


def sort_key(value, numeric=False):
    text = '' if value is None else str(value).strip()
    if numeric:
        try:
            return (0, int(text.replace(',', '')))
        except ValueError:
            return (1, text.casefold())
    return (0, text.casefold())
