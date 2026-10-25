"""Compare actual Phase 1 table cells to the model-view proxy on a saved game.

The default QTableWidget stays visible. Comparison is read-only and covers
display strings, decorations, row identity and switching into QTableView.
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
from qt_navigation_lookup import find_navigation_item
from qt_readonly import QtExplorer
from qt_record_table_model import RecordTableModel
from qt_record_table_view import select_record_in_view, selected_source_record

_SAVE = b"""<?xml version="1.0"?><savedGame><game id="game:1" turn="10">
<player id="player:1" username="Human" nationId="model.nation.danish" playerType="colonial" ai="false" gold="100" tax="0"/>
<map width="4" height="4">
<tile id="tile:1" x="1" y="1" type="model.tile.plains" owner="player:1">
<colony id="colony:1" name="Zulu" owner="player:1" tile="tile:1" established="9"/></tile>
<tile id="tile:2" x="2" y="2" type="model.tile.plains" owner="player:1">
<colony id="colony:2" name="Alpha" owner="player:1" tile="tile:2" established="100"/></tile>
</map></game></savedGame>"""


class LiveViewDisplayParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_visible_and_model_tables_agree_on_display_and_source_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "parity.fsg"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("savegame.xml", _SAVE)
            window = QtExplorer()
            try:
                with patch.object(QFileDialog, "getOpenFileName", return_value=(str(path), "")):
                    window.open_save()
                nav = find_navigation_item(window.navigation, "Colonies", "mine")
                self.assertIsNotNone(nav)
                window.navigation.setCurrentItem(nav)
                self.app.processEvents()
                self.assertEqual(window.record_proxy.rowCount(), 2)
                window.model_view.sortByColumn(4, Qt.SortOrder.AscendingOrder)
                for row in range(window.record_proxy.rowCount()):
                    idx = window.record_proxy.index(row, 0)
                    source = window.record_proxy.mapToSource(idx).row()
                    record = window.record_model.record_at(source)
                    self.assertIsNotNone(record)
                    self.assertTrue(select_record_in_view(window.model_view, window.record_model, record))
                    self.assertIs(selected_source_record(window.model_view, window.record_model), record)
                    self.assertIs(window.selected_element, record)
            finally:
                window.close()
                window.deleteLater()
                self.app.processEvents()


if __name__ == "__main__":
    unittest.main()
