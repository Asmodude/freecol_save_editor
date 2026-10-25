"""Save-backed display parity between accepted table and comparison QTableView."""
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
from qt_record_table_model import RecordTableModel

_SAVE = b"""<?xml version="1.0"?><savedGame><game id="game:1" turn="10">
<player id="player:1" username="Human" nationId="model.nation.danish" playerType="colonial" ai="false" gold="100" tax="0"/>
<map width="4" height="4">
<tile id="tile:1" x="1" y="1" type="model.tile.plains" owner="player:1">
<colony id="colony:1" name="Zulu" owner="player:1" tile="tile:1" established="100"/></tile>
<tile id="tile:2" x="2" y="2" type="model.tile.plains" owner="player:1">
<colony id="colony:2" name="Alpha" owner="player:1" tile="tile:2" established="9"/></tile>
</map></game></savedGame>"""


class LiveComparisonDisplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_colony_cells_match_after_independent_sorting(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "display.fsg"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("savegame.xml", _SAVE)
            window = QtExplorer()
            try:
                with patch.object(QFileDialog, "getOpenFileName", return_value=(str(path), "")):
                    window.open_save()
                target = find_navigation_item(window.navigation, "Colonies", "mine")
                self.assertIsNotNone(target)
                window.navigation.setCurrentItem(target)
                window.set_model_view_comparison(True)
                window.grid.sortItems(1, Qt.SortOrder.DescendingOrder)
                window.model_view.sortByColumn(1, Qt.SortOrder.AscendingOrder)
                self.app.processEvents()
                self.assertEqual(window.grid.rowCount(), window.record_proxy.rowCount())
                for display_row in range(window.grid.rowCount()):
                    cell = window.grid.item(display_row, 0)
                    source_row = cell.data(Qt.ItemDataRole.UserRole)
                    record = window.record_model.record_at(source_row)
                    proxy_row = next(
                        i for i in range(window.record_proxy.rowCount())
                        if window.record_proxy.data(window.record_proxy.index(i, 0), RecordTableModel.RecordRole) is record)
                    for column in range(window.grid.columnCount()):
                        self.assertEqual(window.grid.item(display_row, column).text(),
                                         window.record_proxy.data(window.record_proxy.index(proxy_row, column)))
            finally:
                window.close()
                window.deleteLater()
                self.app.processEvents()


if __name__ == "__main__":
    unittest.main()
