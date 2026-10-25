"""Behavioral tests for shared Qt navigation identity lookup."""
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem
from qt_navigation_lookup import find_navigation_item


class NavigationLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_nested_item_found_by_group_and_scope(self):
        tree = QTreeWidget()
        parent = QTreeWidgetItem(tree, ["Colonies"])
        nested = QTreeWidgetItem(parent, ["Christiansborg"])
        nested.setData(0, Qt.ItemDataRole.UserRole, ("Colonies", "colony-id:17"))
        self.assertIs(find_navigation_item(tree, "Colonies", "colony-id:17"), nested)
        self.assertIsNone(find_navigation_item(tree, "Units", "colony-id:17"))

    def test_top_level_and_missing_lookup(self):
        tree = QTreeWidget()
        item = QTreeWidgetItem(tree, ["My units"])
        item.setData(0, Qt.ItemDataRole.UserRole, ("Units", "mine"))
        self.assertIs(find_navigation_item(tree, "Units", "mine"), item)
        self.assertIsNone(find_navigation_item(tree, "Units", "player:missing"))


if __name__ == "__main__":
    unittest.main()
