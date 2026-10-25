"""Save-backed end-to-end checks for the hidden QTableView in QtExplorer."""
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFileDialog
from qt_navigation_lookup import find_navigation_item
from qt_readonly import QtExplorer
from qt_record_table_view import select_record_in_view, selected_source_record

_SAVE = b"""<?xml version="1.0"?><savedGame><game id="game:1" turn="10">
<player id="player:1" username="Human" nationId="model.nation.danish" playerType="colonial" ai="false" gold="100" tax="0"/>
<map width="4" height="4">
<tile id="tile:1" x="1" y="1" type="model.tile.plains" owner="player:1">
 <colony id="colony:1" name="Zulu" owner="player:1" tile="tile:1"/>
</tile>
<tile id="tile:2" x="2" y="2" type="model.tile.plains" owner="player:1">
 <colony id="colony:2" name="Alpha" owner="player:1" tile="tile:2"/>
</tile></map></game></savedGame>"""


class SaveBackedShadowViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "view.fsg"
        with zipfile.ZipFile(self.path, "w") as archive:
            archive.writestr("savegame.xml", _SAVE)
        self.window = QtExplorer()
        with patch.object(QFileDialog, "getOpenFileName", return_value=(str(self.path), "")):
            self.window.open_save()
        self.app.processEvents()

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def test_shadow_view_preserves_colony_identity_through_sort_and_filter(self):
        w = self.window
        entry = find_navigation_item(w.navigation, "Colonies", "mine")
        self.assertIsNotNone(entry)
        w.navigation.setCurrentItem(entry)
        self.app.processEvents()
        self.assertEqual(w.record_model.rowCount(), 2)
        self.assertEqual(w.model_view.model().rowCount(), 2)
        alpha = next(c for c in w.document.colonies if c.get("name") == "Alpha")
        zulu = next(c for c in w.document.colonies if c.get("name") == "Zulu")
        w.model_view.sortByColumn(1, Qt.SortOrder.AscendingOrder)
        self.assertTrue(select_record_in_view(w.model_view, w.record_model, alpha))
        self.assertIs(selected_source_record(w.model_view, w.record_model), alpha)
        w.record_proxy.setFilterFixedString("Zulu")
        self.assertFalse(select_record_in_view(w.model_view, w.record_model, alpha))
        self.assertTrue(select_record_in_view(w.model_view, w.record_model, zulu))
        self.assertIs(selected_source_record(w.model_view, w.record_model), zulu)
        w.record_proxy.setFilterFixedString("")
        self.assertEqual(w.record_proxy.rowCount(), 2)

    def test_artwork_role_matches_accepted_grid(self):
        w = self.window
        w.navigation.setCurrentItem(find_navigation_item(w.navigation, "Colonies", "mine"))
        self.app.processEvents()
        for row in range(w.record_proxy.rowCount()):
            source = w.record_proxy.mapToSource(w.record_proxy.index(row, 0)).row()
            icon = w.record_model.data(w.record_model.index(source, 0), Qt.ItemDataRole.DecorationRole)
            self.assertIsNotNone(icon)
            self.assertFalse(icon.isNull())


if __name__ == "__main__":
    unittest.main()
