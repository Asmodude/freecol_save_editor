"""Shared navigation-tree record lookup for Qt views.

Search the tree by the stable (group, scope) identity stored in Qt.UserRole.
This module intentionally has no save-editing responsibilities.
"""
from PySide6.QtCore import Qt


def find_navigation_item(tree, group, scope):
    """Find a navigation entry irrespective of its depth or sibling order."""
    identity = (group, scope)

    def visit(item):
        if item.data(0, Qt.ItemDataRole.UserRole) == identity:
            return item
        for index in range(item.childCount()):
            match = visit(item.child(index))
            if match is not None:
                return match
        return None

    for index in range(tree.topLevelItemCount()):
        match = visit(tree.topLevelItem(index))
        if match is not None:
            return match
    return None
