"""Presentation parity for the new proxy without modifying underlying saved values."""
import os
import unittest
from xml.etree.ElementTree import Element

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from qt_record_table_model import RecordTableModel
from qt_record_sort_proxy import RecordSortFilterProxy


class ProxyPresentationParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_colony_established_turn_matches_old_table(self):
        early, late = Element("colony", id="c:1"), Element("colony", id="c:2")
        model = RecordTableModel(("Name", "Established"),
                                 ((late, ("Late", "100")), (early, ("Early", "9"))))
        proxy = RecordSortFilterProxy()
        proxy.setSourceModel(model)
        proxy.set_record_group("Colonies")
        proxy.sort(1, Qt.SortOrder.AscendingOrder)
        self.assertEqual([proxy.data(proxy.index(row, 1)) for row in range(2)],
                         ["Turn 9", "Turn 100"])
        self.assertEqual(model.data(model.index(0, 1)), "100")
        self.assertIs(proxy.data(proxy.index(0, 0), RecordTableModel.RecordRole), early)

    def test_long_game_property_is_shortened_only_in_view(self):
        original = "x" * 130
        record = Element("property", value=original)
        model = RecordTableModel(("Source", "Property", "Saved value"),
                                 ((record, ("Game", "description", original)),))
        proxy = RecordSortFilterProxy()
        proxy.setSourceModel(model)
        proxy.set_record_group("Game properties")
        self.assertEqual(len(proxy.data(proxy.index(0, 2))), 96)
        self.assertTrue(proxy.data(proxy.index(0, 2)).endswith("…"))
        self.assertEqual(model.data(model.index(0, 2)), original)
        self.assertEqual(record.get("value"), original)

    def test_nonformatted_columns_are_unchanged(self):
        model = RecordTableModel(("Gold",), ((Element("player"), ("100",)),))
        proxy = RecordSortFilterProxy()
        proxy.setSourceModel(model)
        proxy.set_record_group("Players")
        self.assertEqual(proxy.data(proxy.index(0, 0)), "100")


if __name__ == "__main__":
    unittest.main()
