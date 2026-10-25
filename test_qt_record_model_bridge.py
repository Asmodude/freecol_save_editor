"""Offscreen integration tests for the staged Qt record-model migration."""
import os
import unittest
from xml.etree.ElementTree import Element

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtWidgets import QApplication
from qt_readonly import QtExplorer


class RecordModelBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_empty_window_mirrors_header_and_rows_without_ui_change(self):
        window = QtExplorer()
        try:
            self.assertEqual(window.record_model.rowCount(), 0)
            self.assertEqual(window.grid.rowCount(), 0)
            self.assertEqual(window.record_model.columnCount(), window.grid.columnCount())
            self.assertEqual(window.record_model.headerData(0, Qt.Orientation.Horizontal), "ID")
            window.group = "Units"
            window.populate()
            self.assertEqual(window.record_model.columnCount(), window.grid.columnCount())
            self.assertEqual(window.record_model.rowCount(), window.grid.rowCount())
            self.assertIsNone(window.record_model.record_at(0))
        finally:
            window.close()

    def test_model_preserves_element_identity_through_sorting(self):
        window = QtExplorer()
        try:
            left = Element("unit", id="unit:left")
            right = Element("unit", id="unit:right")
            window.record_model.replace_rows(
                ((left, ("Zulu",)), (right, ("Alpha",))), ("Name",))
            proxy = QSortFilterProxyModel()
            proxy.setSourceModel(window.record_model)
            proxy.sort(0)
            source_row = proxy.mapToSource(proxy.index(0, 0)).row()
            self.assertIs(window.record_model.record_at(source_row), right)
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
