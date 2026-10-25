"""Exercise the hidden QTableView inside the actual QtExplorer lifecycle."""
import os
import unittest
from xml.etree.ElementTree import Element

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from qt_readonly import QtExplorer
from qt_record_table_view import selected_source_record, select_record_in_view


class LiveShadowTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_new_view_exists_without_replacing_accepted_grid(self):
        window = QtExplorer()
        try:
            self.assertIs(window.model_view.model(), window.record_proxy)
            self.assertIs(window.record_proxy.sourceModel(), window.record_model)
            self.assertIsNotNone(window.model_view)
            self.assertFalse(hasattr(window, "grid"))
            self.assertEqual(window.record_model.rowCount(), window.model_view.model().rowCount())
            window.group = "Units"
            window.populate()
            self.assertEqual(window.model_view.iconSize().width(), 42)
            self.assertEqual(window.model_view.model().rowCount(), window.record_model.rowCount())
            self.assertIsNotNone(window.model_view)
        finally:
            window.close()

    def test_shadow_selection_uses_same_authoritative_record_identity(self):
        window = QtExplorer()
        try:
            a, b = Element("unit", id="u:a"), Element("unit", id="u:b")
            window.record_model.replace_rows(
                ((a, ("Zulu",)), (b, ("Alpha",))), ("Name",))
            window.model_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
            self.assertTrue(select_record_in_view(window.model_view, window.record_model, a))
            self.assertIs(selected_source_record(window.model_view, window.record_model), a)
            self.assertIsNotNone(window.model_view)
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
