"""Regression: comparison Inspector must reject a record absent from current scope."""
import os
import unittest
from xml.etree.ElementTree import Element
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication

from qt_readonly import QtExplorer
from qt_record_table_view import select_record_in_view


class StaleComparisonSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_stale_selection_cannot_replace_current_inspected_record(self):
        window = QtExplorer()
        try:
            stale = Element("colony", id="colony:stale")
            current = Element("colony", id="colony:current")
            window._compare_model_view = True
            window.document = object()
            window.visible_rows = [current]
            window.record_model.replace_rows(((stale, ("Stale",)),), ("Name",))
            # Suppress selection-triggered Inspector calls until the setup is complete.
            with patch.object(window, "update_detail_tabs", side_effect=AssertionError("stale inspection")):
                self.assertTrue(select_record_in_view(window.model_view, window.record_model, stale))
                window.selected_element = None
                window.inspect()
                self.assertIsNone(window.selected_element)
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
