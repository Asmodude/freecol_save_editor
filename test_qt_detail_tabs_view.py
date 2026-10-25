"""Behavioral coverage for extracted read-only detail tab view."""
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication
from qt_readonly import QtExplorer
from qt_detail_tabs_view import DetailTabsMixin


class DetailTabsViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_empty_selection_has_only_overview_and_no_drilldown(self):
        window = QtExplorer()
        try:
            self.assertIsInstance(window, DetailTabsMixin)
            window.group = "Players"
            window.update_detail_tabs(None)
            self.assertEqual([window.tabs.tabText(i) for i in range(window.tabs.count())], ["Overview"])
            self.assertFalse(window.jump_unit_button.isVisible())
            self.assertFalse(window.jump_colony_button.isVisible())
        finally:
            window.close()

    def test_contextual_colony_button_disabled_outside_goods(self):
        window = QtExplorer()
        try:
            window.group = "Players"
            window.refresh_breakdown_action(0)
            self.assertFalse(window.jump_colony_button.isEnabled())
            self.assertFalse(window.jump_colony_button.isVisible())
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
