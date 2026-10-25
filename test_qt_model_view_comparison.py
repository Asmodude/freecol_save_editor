"""Offscreen opt-in comparison of accepted table and QTableView."""
import os
import unittest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication
from qt_readonly import QtExplorer


class ModelViewComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_comparison_can_be_enabled_and_reverted(self):
        window = QtExplorer()
        try:
            window.show()
            self.app.processEvents()
            self.assertTrue(window.grid.isVisible())
            self.assertFalse(window.model_view.isVisible())
            window.set_model_view_comparison(True)
            self.app.processEvents()
            self.assertFalse(window.grid.isVisible())
            self.assertTrue(window.model_view.isVisible())
            self.assertIs(window.model_view.model(), window.record_proxy)
            window.set_model_view_comparison(False)
            self.app.processEvents()
            self.assertTrue(window.grid.isVisible())
            self.assertFalse(window.model_view.isVisible())
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
