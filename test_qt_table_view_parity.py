"""Offscreen sizing and selection parity between Qt's two table types."""
import os
import unittest
from xml.etree.ElementTree import Element
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem
from qt_record_table_model import RecordTableModel
from qt_record_table_view import (
    build_record_table_view, apply_record_view_sizing,
    selected_source_record, select_record_in_view, select_record_in_legacy_table,
)


class ViewParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_sizes_match_approved_unit_and_colony_rows(self):
        model = RecordTableModel(("Name",), ((Element("unit"), ("Infantry",)),))
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        view = build_record_table_view(proxy)
        try:
            apply_record_view_sizing(view, "Units")
            self.assertEqual(view.rowHeight(0), 44)
            self.assertEqual(view.iconSize().width(), 42)
            apply_record_view_sizing(view, "Colonies")
            self.assertEqual(view.rowHeight(0), 36)
            self.assertEqual(view.iconSize().height(), 30)
            apply_record_view_sizing(view, "Founding Fathers")
            self.assertEqual(view.rowHeight(0), 75)
        finally:
            view.close()

    def test_sorted_legacy_selection_synchronises_by_source_identity(self):
        a, b = Element("unit", id="u:a"), Element("unit", id="u:b")
        model = RecordTableModel(("Name",), ((a, ("Alpha",)), (b, ("Zulu",))))
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        view = build_record_table_view(proxy)
        legacy = QTableWidget(2, 1)
        try:
            for row, name in enumerate(("Zulu", "Alpha")):
                item = QTableWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, 1 - row)
                legacy.setItem(row, 0, item)
            self.assertTrue(select_record_in_view(view, model, b))
            self.assertTrue(select_record_in_legacy_table(legacy, model, b))
            self.assertIs(selected_source_record(view, model), b)
            self.assertEqual(legacy.currentRow(), 0)
            self.assertFalse(select_record_in_legacy_table(legacy, model, Element("unit", id="u:b")))
        finally:
            legacy.close()
            view.close()


if __name__ == "__main__":
    unittest.main()
