"""Offscreen proxy integration against live Qt record model."""
import os
import unittest
from xml.etree.ElementTree import Element

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from qt_readonly import QtExplorer
from qt_record_table_model import RecordTableModel


class RecordProxyIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_proxy_filters_multiple_columns_without_changing_source(self):
        window = QtExplorer()
        try:
            left = Element("colony", id="colony:1")
            right = Element("colony", id="colony:2")
            window.record_model.replace_rows(
                ((left, ("Zulu", "Dutch")), (right, ("Alpha", "Danish"))),
                ("Name", "Nation"))
            proxy = window.record_proxy
            self.assertIs(proxy.sourceModel(), window.record_model)
            proxy.setFilterFixedString("danish")
            self.assertEqual(proxy.rowCount(), 1)
            self.assertIs(proxy.data(proxy.index(0, 0), RecordTableModel.RecordRole), right)
            self.assertEqual(window.record_model.rowCount(), 2)
            proxy.setFilterFixedString("")
            proxy.sort(0, Qt.SortOrder.DescendingOrder)
            self.assertEqual(proxy.rowCount(), 2)
            self.assertIs(proxy.data(proxy.index(0, 0), RecordTableModel.RecordRole), left)
        finally:
            window.close()

    def test_model_reset_invalidates_old_proxy_indices(self):
        window = QtExplorer()
        try:
            window.record_model.replace_rows(
                ((Element("unit", id="u:1"), ("One",)),), ("Name",))
            old = window.record_proxy.index(0, 0)
            self.assertTrue(old.isValid())
            window.record_model.replace_rows((), ("Name",))
            self.assertEqual(window.record_proxy.rowCount(), 0)
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
