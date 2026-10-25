"""Behavioral parity for QTableView selection through sorting and filtering."""
import os
import unittest
from xml.etree.ElementTree import Element

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtWidgets import QApplication
from qt_record_table_model import RecordTableModel
from qt_record_table_view import (
    build_record_table_view, selected_source_record, select_record_in_view,
)


class TableViewSelectionParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_identity_selection_after_sort_and_filter(self):
        one, two = Element("colony", id="colony:1"), Element("colony", id="colony:2")
        model = RecordTableModel(("Name", "Owner"), ((one, ("Zulu", "Danish")), (two, ("Alpha", "Dutch"))))
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        proxy.setFilterKeyColumn(-1)
        view = build_record_table_view(proxy)
        try:
            view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
            self.assertTrue(select_record_in_view(view, model, one))
            self.assertIs(selected_source_record(view, model), one)
            proxy.setFilterFixedString("Dutch")
            self.assertFalse(select_record_in_view(view, model, one))
            self.assertTrue(select_record_in_view(view, model, two))
            self.assertIs(selected_source_record(view, model), two)
            proxy.setFilterFixedString("")
            view.sortByColumn(0, Qt.SortOrder.DescendingOrder)
            self.assertTrue(select_record_in_view(view, model, one))
            self.assertIs(selected_source_record(view, model), one)
        finally:
            view.close()

    def test_missing_record_is_not_replaced_by_neighbour(self):
        actual = Element("unit", id="u:1")
        different_object_same_id = Element("unit", id="u:1")
        model = RecordTableModel(("Name",), ((actual, ("Infantry",)),))
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        view = build_record_table_view(proxy)
        try:
            self.assertFalse(select_record_in_view(view, model, different_object_same_id))
            self.assertIsNone(selected_source_record(view, model))
        finally:
            view.close()


if __name__ == "__main__":
    unittest.main()
