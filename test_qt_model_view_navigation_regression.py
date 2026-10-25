"""Phase 2A: save-backed navigation and model-view comparison regression.

Switching contexts after sorting/filtering must not leave stale selection or
route the Inspector to a record belonging to the previous view.
"""
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
from qt_record_table_view import select_record_in_view, selected_source_record

_SAVE = b"""<?xml version="1.0"?><savedGame><game id="game:1" turn="10">
<player id="player:1" username="Human" nationId="model.nation.danish"
 playerType="colonial" ai="false" gold="100" tax="0"/>
<map width="4" height="4">
<tile id="tile:1" x="1" y="1" type="model.tile.plains" owner="player:1">
 <colony id="colony:1" name="Zulu" owner="player:1" tile="tile:1"/></tile>
<tile id="tile:2" x="2" y="2" type="model.tile.plains" owner="player:1">
 <colony id="colony:2" name="Alpha" owner="player:1" tile="tile:2"/></tile>
</map></game></savedGame>"""


class NavigationModelViewRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_switching_groups_discards_stale_model_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "navigation.fsg"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("savegame.xml", _SAVE)
            window = QtExplorer()
            try:
                with patch.object(QFileDialog, "getOpenFileName", return_value=(str(path), "")):
                    window.open_save()
                colonies = find_navigation_item(window.navigation, "Colonies", "mine")
                players = find_navigation_item(window.navigation, "Players", "mine")
                self.assertIsNotNone(colonies)
                self.assertIsNotNone(players)
                window.navigation.setCurrentItem(colonies)
                window.model_view.sortByColumn(1, Qt.SortOrder.DescendingOrder)
                chosen = next(c for c in window.document.colonies if c.get("name") == "Alpha")
                self.assertTrue(select_record_in_view(window.model_view, window.record_model, chosen))
                self.assertIs(window.selected_element, chosen)
                window.navigation.setCurrentItem(players)
                self.app.processEvents()
                self.assertEqual(window.group, "Players")
                self.assertEqual(window.record_model.rowCount(), window.record_proxy.rowCount())
                self.assertIsNot(window.selected_element, chosen)
                self.assertIsNot(selected_source_record(window.model_view, window.record_model), chosen)
                self.assertEqual(window.record_proxy.rowCount(), window.record_model.rowCount())
            finally:
                window.close()
                window.deleteLater()
                self.app.processEvents()


if __name__ == "__main__":
    unittest.main()
