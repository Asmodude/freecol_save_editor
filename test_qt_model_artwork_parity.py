"""Verify accepted QTableWidget icon presentation is mirrored into Qt model."""
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

_SAVE = b"""<?xml version="1.0"?><savedGame><game id="game:1" turn="10">
<player id="player:1" username="Human" nationId="model.nation.danish" playerType="colonial" ai="false" gold="100" tax="0"/>
<map width="4" height="4"><tile id="tile:1" x="1" y="1" type="model.tile.plains" owner="player:1">
<colony id="colony:1" name="Christiansborg" owner="player:1" tile="tile:1"/>
</tile></map></game></savedGame>"""


class ModelArtworkParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_model_decorations_follow_legacy_icons_after_sort(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "artwork.fsg"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("savegame.xml", _SAVE)
            window = QtExplorer()
            try:
                with patch.object(QFileDialog, "getOpenFileName", return_value=(str(path), "")):
                    window.open_save()
                for group in ("Players", "Colonies", "National Goods"):
                    with self.subTest(group=group):
                        target = find_navigation_item(window.navigation, group, "mine")
                        self.assertIsNotNone(target)
                        window.navigation.setCurrentItem(target)
                        self.app.processEvents()
                        window.grid.sortItems(0, Qt.SortOrder.DescendingOrder)
                        for visible_row in range(window.grid.rowCount()):
                            for column in range(window.grid.columnCount()):
                                cell = window.grid.item(visible_row, column)
                                source_row = cell.data(Qt.ItemDataRole.UserRole)
                                model_index = window.record_model.index(source_row, column)
                                decoration = window.record_model.data(model_index, Qt.ItemDataRole.DecorationRole)
                                self.assertEqual(decoration is None, cell.icon().isNull())
                                if decoration is not None:
                                    self.assertEqual(decoration.cacheKey(), cell.icon().cacheKey())
                                self.assertEqual(
                                    window.record_model.data(model_index, Qt.ItemDataRole.ToolTipRole),
                                    cell.toolTip() or None)
            finally:
                window.close()
                window.deleteLater()
                self.app.processEvents()


if __name__ == "__main__":
    unittest.main()
