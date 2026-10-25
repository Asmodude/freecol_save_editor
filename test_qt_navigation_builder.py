"""Behavioral smoke checks for the extracted Qt navigation-tree builder."""
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from qt_readonly import QtExplorer
from qt_navigation_lookup import find_navigation_item


class NavigationBuilderBehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_empty_document_has_expected_navigation_and_default_selection(self):
        explorer = QtExplorer()
        try:
            self.assertIsNotNone(find_navigation_item(explorer.navigation, "Players", "mine"))
            self.assertIsNotNone(find_navigation_item(explorer.navigation, "Game properties", "game"))
            chosen = explorer.navigation.currentItem()
            self.assertEqual(chosen.data(0, Qt.ItemDataRole.UserRole), ("Players", "mine"))
            self.assertIsNone(find_navigation_item(explorer.navigation, "Units", "player:missing"))
        finally:
            explorer.close()

    def test_navigation_rebuild_preserves_initial_selection(self):
        explorer = QtExplorer()
        try:
            explorer.install_navigation()
            self.assertEqual(
                explorer.navigation.currentItem().data(0, Qt.ItemDataRole.UserRole),
                ("Players", "mine"),
            )
        finally:
            explorer.close()


if __name__ == "__main__":
    unittest.main()
