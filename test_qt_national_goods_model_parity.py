"""Integration test: National Goods displayed cells remain model-identical."""
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
<colony id="colony:1" name="Christiansborg" owner="player:1" tile="tile:1">
<goodsContainer id="gc:1"><storedGoods><goods type="model.goods.food" amount="120"/></storedGoods></goodsContainer>
</colony></tile></map></game></savedGame>"""


class NationalGoodsModelParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_displayed_goods_are_model_backed_even_after_sort(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "goods.fsg"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("savegame.xml", _SAVE)
            window = QtExplorer()
            try:
                with patch.object(QFileDialog, "getOpenFileName", return_value=(str(path), "")):
                    window.open_save()
                target = find_navigation_item(window.navigation, "National Goods", "mine")
                self.assertIsNotNone(target)
                window.navigation.setCurrentItem(target)
                self.app.processEvents()
                self.assertGreater(window.grid.rowCount(), 0)
                self.assertEqual(window.grid.rowCount(), window.record_model.rowCount())
                window.grid.sortItems(0, Qt.SortOrder.DescendingOrder)
                for displayed_row in range(window.grid.rowCount()):
                    first = window.grid.item(displayed_row, 0)
                    source_row = first.data(Qt.ItemDataRole.UserRole)
                    self.assertIs(window.record_model.record_at(source_row),
                                  window.visible_rows[source_row])
                    for column in range(3):
                        self.assertEqual(window.grid.item(displayed_row, column).text(),
                                         window.record_model.data(window.record_model.index(source_row, column)))
                window.grid.selectRow(0)
                self.app.processEvents()
                source_row = window.grid.item(0, 0).data(Qt.ItemDataRole.UserRole)
                self.assertIs(window.selected_element, window.record_model.record_at(source_row))
            finally:
                window.close()
                window.deleteLater()
                self.app.processEvents()


if __name__ == "__main__":
    unittest.main()
