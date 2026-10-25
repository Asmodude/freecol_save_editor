"""Exercise QTableView/proxy selection using real Qt objects offscreen."""
import os
import unittest
from xml.etree.ElementTree import Element

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtWidgets import QApplication
from qt_record_table_model import RecordTableModel
from qt_record_table_view import build_record_table_view, selected_source_record


class TableViewMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_sorted_proxy_selection_maps_to_source_record(self):
        alpha, zulu = Element("unit", id="u:a"), Element("unit", id="u:z")
        model = RecordTableModel(("Name", "Owner"), ((zulu, ("Zulu", "Danish")), (alpha, ("Alpha", "Dutch"))))
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        view = build_record_table_view(proxy)
        try:
            view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
            view.setCurrentIndex(proxy.index(0, 0))
            self.assertIs(selected_source_record(view, model), alpha)
            view.sortByColumn(0, Qt.SortOrder.DescendingOrder)
            view.setCurrentIndex(proxy.index(0, 0))
            self.assertIs(selected_source_record(view, model), zulu)
            self.assertFalse(bool(model.flags(model.index(0, 0)) & Qt.ItemFlag.ItemIsEditable))
        finally:
            view.close()

    def test_filter_preserves_identity_and_missing_selection_is_safe(self):
        alpha, zulu = Element("unit", id="u:a"), Element("unit", id="u:z")
        model = RecordTableModel(("Name",), ((alpha, ("Alpha",)), (zulu, ("Zulu",))))
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        view = build_record_table_view(proxy)
        try:
            proxy.setFilterFixedString("Zulu")
            view.setCurrentIndex(proxy.index(0, 0))
            self.assertIs(selected_source_record(view, model), zulu)
            proxy.setFilterFixedString("No match")
            self.assertEqual(proxy.rowCount(), 0)
            self.assertIsNone(selected_source_record(view, model))
        finally:
            view.close()


if __name__ == "__main__":
    unittest.main()
