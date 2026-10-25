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
                        window.model_view.sortByColumn(0, Qt.SortOrder.DescendingOrder)
                        for visible_row in range(window.record_proxy.rowCount()):
                            proxy_index = window.record_proxy.index(visible_row, 0)
                            source_index = window.record_proxy.mapToSource(proxy_index)
                            self.assertTrue(source_index.isValid())
                            icon = window.record_proxy.data(proxy_index, Qt.ItemDataRole.DecorationRole)
                            self.assertIsNotNone(icon)
                            self.assertFalse(icon.isNull())
                            self.assertIs(window.record_model.record_at(source_index.row()),
                                          window.visible_rows[source_index.row()])
            finally:
                window.close()
                window.deleteLater()
                self.app.processEvents()


if __name__ == "__main__":
    unittest.main()
