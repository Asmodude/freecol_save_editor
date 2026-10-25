"""Behavioral parity for numeric and textual columns in Phase 2A proxy."""
import os
import unittest
from xml.etree.ElementTree import Element

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from qt_record_table_model import RecordTableModel
from qt_record_sort_proxy import RecordSortFilterProxy


class RecordSortProxyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_players_gold_sorts_numerically(self):
        a, b, c = (Element("player", id=f"p:{i}") for i in range(3))
        model = RecordTableModel(
            ("Username", "Gold"),
            ((a, ("Zulu", "9")), (b, ("Bravo", "100")), (c, ("Alpha", "21"))))
        proxy = RecordSortFilterProxy()
        proxy.setSourceModel(model)
        proxy.set_record_group("Players")
        proxy.sort(1, Qt.SortOrder.AscendingOrder)
        self.assertEqual([proxy.data(proxy.index(row, 1)) for row in range(3)],
                         ["9", "21", "100"])
        self.assertIs(proxy.data(proxy.index(0, 0), RecordTableModel.RecordRole), a)

    def test_textual_ids_are_not_coerced_to_numbers(self):
        model = RecordTableModel(
            ("ID",), tuple((Element("unit", id=name), (name,)) for name in ("unit:9", "unit:10")))
        proxy = RecordSortFilterProxy()
        proxy.setSourceModel(model)
        proxy.set_record_group("Units")
        proxy.sort(0, Qt.SortOrder.AscendingOrder)
        self.assertEqual([proxy.data(proxy.index(i, 0)) for i in range(2)],
                         ["unit:10", "unit:9"])

    def test_group_change_reinterprets_column(self):
        model = RecordTableModel(("Gold",), ((Element("x"), ("9",)), (Element("x"), ("100",))))
        proxy = RecordSortFilterProxy()
        proxy.setSourceModel(model)
        proxy.set_record_group("Players")
        proxy.sort(0)
        self.assertEqual(proxy.data(proxy.index(0, 0)), "9")
        proxy.set_record_group("Units")
        proxy.sort(0)
        self.assertEqual(proxy.data(proxy.index(0, 0)), "100")


if __name__ == "__main__":
    unittest.main()
