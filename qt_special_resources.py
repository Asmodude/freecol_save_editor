"""FreeCol progress/production goods must not masquerade as warehouse inventory.

These IDs are retained in the embedded specification and original save XML.
Only Qt warehouse list/catalog aggregation excludes them.
"""
VIRTUAL_GOODS = frozenset({
    'model.goods.bells',
    'model.goods.crosses',
    'model.goods.hammers',
})


def is_warehouse_good(kind):
    return bool(kind) and kind not in VIRTUAL_GOODS
