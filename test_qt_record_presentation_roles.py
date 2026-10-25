"""Offscreen model/view presentation parity: role data follows source records."""
import os
import unittest
from xml.etree.ElementTree import Element
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication
from qt_record_table_model import RecordTableModel
from qt_record_table_view import build_record_table_view, selected_source_record


class PresentationRoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_icons_and_tooltips_follow_records_after_sort(self):
        a, z = Element("colony", id="a"), Element("colony", id="z")
        model = RecordTableModel(("Name",), ((z, ("Zulu",)), (a, ("Alpha",))))
        icon = QIcon(QPixmap(12, 12))
        model.set_presentation({(0, 0): icon}, {(0, 0): "Zulu colony"})
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        view = build_record_table_view(proxy)
        try:
            view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
            self.assertEqual(proxy.data(proxy.index(1, 0), Qt.ItemDataRole.ToolTipRole), "Zulu colony")
            self.assertIsInstance(proxy.data(proxy.index(1, 0), Qt.ItemDataRole.DecorationRole), QIcon)
            view.setCurrentIndex(proxy.index(1, 0))
            self.assertIs(selected_source_record(view, model), z)
            model.replace_rows(((a, ("Alpha",)),), ("Name",))
            self.assertIsNone(model.data(model.index(0, 0), Qt.ItemDataRole.ToolTipRole))
            self.assertIsNone(model.data(model.index(0, 0), Qt.ItemDataRole.DecorationRole))
        finally:
            view.close()

    def test_presentation_metadata_never_edits_xml(self):
        record = Element("unit", id="unit:1", experience="22")
        model = RecordTableModel(("Experience",), ((record, ("22",)),))
        model.set_presentation(tooltips={(0, 0): "Original value"})
        self.assertEqual(record.get("experience"), "22")
        self.assertFalse(bool(model.flags(model.index(0, 0)) & Qt.ItemFlag.ItemIsEditable))


if __name__ == "__main__":
    unittest.main()
