"""Offscreen end-to-end Inspector parity in opt-in QTableView comparison mode."""
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFileDialog
from qt_readonly import QtExplorer
from qt_navigation_lookup import find_navigation_item
from qt_record_table_view import select_record_in_view

_SAVE = b"""<?xml version="1.0"?><savedGame><game id="game:1" turn="10">
<player id="player:1" username="Human" nationId="model.nation.danish" playerType="colonial" ai="false" gold="100" tax="0"/>
<map width="4" height="4">
<tile id="tile:1" x="1" y="1" type="model.tile.plains" owner="player:1">
<colony id="colony:1" name="Zulu" owner="player:1" tile="tile:1"/></tile>
<tile id="tile:2" x="2" y="2" type="model.tile.plains" owner="player:1">
<colony id="colony:2" name="Alpha" owner="player:1" tile="tile:2"/></tile>
</map></game></savedGame>"""


class ComparisonInspectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_inspector_tracks_sorted_model_view_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "comparison.fsg"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("savegame.xml", _SAVE)
            window = QtExplorer()
            try:
                with patch.object(QFileDialog, "getOpenFileName", return_value=(str(path), "")):
                    window.open_save()
                window.navigation.setCurrentItem(find_navigation_item(window.navigation, "Colonies", "mine"))
                window.set_model_view_comparison(True)
                window.model_view.sortByColumn(1, Qt.SortOrder.DescendingOrder)
                self.app.processEvents()
                for record in window.document.colonies:
                    self.assertTrue(select_record_in_view(window.model_view, window.record_model, record))
                    self.app.processEvents()
                    self.assertIs(window.selected_element, record)
                    self.assertIn(record.get("name"), window.inspector_label.text())
                window.set_model_view_comparison(False)
                self.assertFalse(window._compare_model_view)
                self.assertEqual(window.grid.rowCount(), 2)
            finally:
                window.close()
                window.deleteLater()
                self.app.processEvents()


if __name__ == "__main__":
    unittest.main()
