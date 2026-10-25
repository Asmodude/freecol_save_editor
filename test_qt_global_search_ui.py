"""Behavioral regression tests for extracted global-search and sorting components."""
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication, QTableWidget
from qt_sortable_item import SortableItem
from qt_readonly import QtExplorer
from qt_global_search_ui import GlobalSearchMixin


class ExtractedSearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_sortable_item_keeps_numeric_comparison(self):
        table = QTableWidget(2, 1)
        table.setItem(0, 0, SortableItem("10", numeric=True))
        table.setItem(1, 0, SortableItem("2", numeric=True))
        table.sortItems(0)
        self.assertEqual([table.item(r, 0).text() for r in range(2)], ["2", "10"])

    def test_main_window_uses_extracted_search_component(self):
        self.assertTrue(issubclass(QtExplorer, GlobalSearchMixin))
        window = QtExplorer()
        try:
            self.assertIsNone(window.document)
            # Without a loaded document, searching is a harmless no-op.
            self.assertIsNone(window.open_global_search())
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
