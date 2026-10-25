"""Offscreen behavioral checks for the extracted diplomacy view."""
import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication
from qt_readonly import QtExplorer
from qt_diplomacy_view import DiplomacyViewMixin


class DiplomacyViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_diplomacy_view_preserves_separate_categories(self):
        window = QtExplorer()
        try:
            self.assertIsInstance(window, DiplomacyViewMixin)
            self.assertEqual(set(window.diplomacy_grids), {"Rival Nations", "Natives"})
            self.assertEqual(window.diplomacy_tabs.count(), 2)
        finally:
            window.close()

    def test_diplomacy_inspect_is_noop_outside_diplomacy(self):
        window = QtExplorer()
        try:
            for category in window.diplomacy_grids:
                self.assertIsNone(window.inspect_diplomacy(category))
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
