"""Bound lengthy game-property display text without modifying saved values."""

def compact_property_value(value, limit=96):
    text='' if value is None else str(value)
    if len(text)<=limit:
        return text
    if limit<12:
        raise ValueError('Display limit must be at least 12')
    return text[:limit-1] + '…'
