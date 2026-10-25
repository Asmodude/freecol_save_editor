"""Contextual unit navigation targets the model view when comparison is active."""
import os
import unittest
from unittest.mock import MagicMock, patch
from xml.etree.ElementTree import Element

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication
from qt_readonly import QtExplorer
from qt_record_table_view import selected_source_record


class ContextualUnitViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_contextual_unit_drilldown_selects_original_record(self):
        window = QtExplorer()
        try:
            unit = Element("unit", id="unit:55", owner="player:1")
            document = MagicMock()
            document.unit_by_id.return_value = unit
            document.players = {"player:1": Element("player", id="player:1", ai="false")}
            window.document = document
            window.detail_unit_id = "unit:55"
            window._compare_model_view = True
            window.group = "Units"
            window.scope = "mine"
            window.record_model.replace_rows(((unit, ("unit:55",)),), ("ID",))
            with patch("qt_readonly.human_player_id", return_value="player:1"), patch(
                "qt_readonly.find_navigation_item", return_value=window.navigation.currentItem()
            ):
                # Keep the model content stable while testing the actual drill-down.
                with patch.object(window, "populate", return_value=None):
                    window.open_detail_unit()
            self.assertIs(selected_source_record(window.model_view, window.record_model), unit)
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
