"""Offscreen parity tests for first visible Qt model-backed columns."""
import os
import unittest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from qt_readonly import QtExplorer
from qt_record_table_model import RecordTableModel


class ModelBackedPropertyColumnsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_game_property_columns_match_model_even_when_sorted(self):
        window = QtExplorer()
        try:
            window.group = "Game properties"
            window.record_model.replace_rows(
                (("record:2", ("Game", "zeta", "123")),
                 ("record:1", ("Map", "alpha", "456"))),
                ("Source", "Property", "Saved value"))
            # The first two columns use exactly the same public model data
            # contract as the model-backed population path.
            for row in range(window.record_model.rowCount()):
                for col in (0, 1):
                    index = window.record_model.index(row, col)
                    self.assertEqual(window.record_model.data(index, Qt.ItemDataRole.DisplayRole),
                                     ("Game", "zeta")[col] if row == 0 else ("Map", "alpha")[col])
            self.assertFalse(bool(window.record_model.flags(window.record_model.index(0, 0)) &
                                  Qt.ItemFlag.ItemIsEditable))
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
