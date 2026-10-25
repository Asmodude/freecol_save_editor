"""Offscreen tests for record identity across legacy-table selection and proxy filtering."""
import os
import unittest
from xml.etree.ElementTree import Element
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtWidgets import QApplication
from qt_readonly import QtExplorer
from qt_record_table_model import RecordTableModel


class RecordSelectionIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_proxy_filter_and_sort_retain_source_identity(self):
        records = [Element("unit", id=x) for x in ("unit:z", "unit:a", "unit:b")]
        model = RecordTableModel(("Name",), tuple(zip(records, (("Zulu",), ("Alpha",), ("Bravo",)))))
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        proxy.setFilterFixedString("a")
        proxy.sort(0, Qt.SortOrder.DescendingOrder)
        self.assertEqual(proxy.rowCount(), 2)
        self.assertIs(proxy.data(proxy.index(0, 0), RecordTableModel.RecordRole), records[2])
        self.assertIs(proxy.data(proxy.index(1, 0), RecordTableModel.RecordRole), records[1])

    def test_inspector_rejects_mismatched_model_record(self):
        window = QtExplorer()
        try:
            a, b = Element("unit", id="unit:a"), Element("unit", id="unit:b")
            window.document = object()
            window.group = "Units"
            window.visible_rows = [a]
            window.record_model.replace_rows(((b, ("Other",)),), ("Name",))
            window.model_view.setCurrentIndex(window.record_proxy.index(0, 0))
            window.selected_element = None
            window.inspect()
            self.assertIsNone(window.selected_element)
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
