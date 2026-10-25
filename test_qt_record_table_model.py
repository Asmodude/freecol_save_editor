"""Offscreen tests for the future model/view record table foundation."""
import os
import unittest
from xml.etree.ElementTree import Element

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtWidgets import QApplication
from qt_record_table_model import RecordTableModel


class RecordModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_staged_background_distinguishes_field_and_resets(self):
        from PySide6.QtCore import Qt
        from xml.etree.ElementTree import Element
        from qt_record_table_model import RecordTableModel
        record = Element('player', {'id': 'player:19'})
        model = RecordTableModel(('Name', 'Gold'), ((record, ('Morten', '9000')),))
        model.set_presentation(staged_cells={(0, 1)})
        self.assertIsNone(model.data(model.index(0, 0), Qt.ItemDataRole.BackgroundRole))
        self.assertIsNotNone(model.data(model.index(0, 1), Qt.ItemDataRole.BackgroundRole))
        model.replace_rows(((record, ('Morten', '7225')),), ('Name', 'Gold'))
        self.assertIsNone(model.data(model.index(0, 1), Qt.ItemDataRole.BackgroundRole))

    def test_record_identity_survives_proxy_sort(self):
        first = Element("unit", id="unit:2")
        second = Element("unit", id="unit:1")
        model = RecordTableModel(("Name",), ((first, ("Zulu",)), (second, ("Alpha",))))
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        proxy.sort(0)
        self.assertEqual(proxy.data(proxy.index(0, 0)), "Alpha")
        self.assertIs(proxy.data(proxy.index(0, 0), RecordTableModel.RecordRole), second)

    def test_model_is_read_only_and_resettable(self):
        record = Element("player", id="player:1")
        model = RecordTableModel(("Gold",), ((record, (100,)),))
        index = model.index(0, 0)
        self.assertEqual(model.data(index), "100")
        self.assertFalse(bool(model.flags(index) & Qt.ItemFlag.ItemIsEditable))
        model.replace_rows(())
        self.assertEqual(model.rowCount(), 0)
        self.assertEqual(record.get("id"), "player:1")


if __name__ == "__main__":
    unittest.main()
