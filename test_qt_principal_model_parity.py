"""Phase 2A: model-backed display parity for the three principal record groups.

Use a real FreeCol save ZIP and assert model data survives the visible
QTableWidget's sorting and original-row identity mapping.
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

from qt_readonly import QtExplorer, HEADERS
from qt_navigation_lookup import find_navigation_item
from qt_final_visual_format import established_turn

_SAVE = b"""<?xml version="1.0"?><savedGame><game id="game:1" turn="10">
<player id="player:1" username="Human" nationId="model.nation.danish" playerType="colonial" ai="false" gold="100" tax="0"/>
<map width="4" height="4">
<tile id="tile:1" x="1" y="1" type="model.tile.plains" owner="player:1">
<colony id="colony:1" name="Zulu" owner="player:1" tile="tile:1" established="3"/></tile>
<tile id="tile:2" x="2" y="2" type="model.tile.plains" owner="player:1">
<colony id="colony:2" name="Alpha" owner="player:1" tile="tile:2" established="5"/></tile>
</map></game></savedGame>"""


class PrincipalModelParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_player_colony_and_unit_display_model_parity(self):
        with tempfile.TemporaryDirectory() as temp:
            filename = Path(temp) / "parity.fsg"
            with zipfile.ZipFile(filename, "w") as archive:
                archive.writestr("savegame.xml", _SAVE)
            window = QtExplorer()
            try:
                with patch.object(QFileDialog, "getOpenFileName", return_value=(str(filename), "")):
                    window.open_save()
                for group in ("Players", "Colonies", "Units"):
                    with self.subTest(group=group):
                        target = find_navigation_item(window.navigation, group, "mine")
                        self.assertIsNotNone(target)
                        window.navigation.setCurrentItem(target)
                        self.app.processEvents()
                        self.assertEqual(window.record_proxy.rowCount(), window.record_model.rowCount())
                        self.assertEqual(window.record_proxy.columnCount(), window.record_model.columnCount())
                        window.model_view.sortByColumn(0, Qt.SortOrder.DescendingOrder)
                        for visible in range(window.record_proxy.rowCount()):
                            source = window.record_proxy.mapToSource(window.record_proxy.index(visible, 0)).row()
                            self.assertIs(window.record_model.record_at(source), window.visible_rows[source])
                            for column in range(window.record_proxy.columnCount()):
                                value = window.record_model.data(window.record_model.index(source, column))
                                if group == "Colonies" and HEADERS[group][column] == "Established":
                                    value = established_turn(value)
                                self.assertEqual(window.record_proxy.data(window.record_proxy.index(visible, column)), value)
                        if window.record_proxy.rowCount():
                            window.model_view.selectRow(0)
                            window.model_view.setCurrentIndex(window.record_proxy.index(0, 0))
                            self.app.processEvents()
                            source = window.record_proxy.mapToSource(window.record_proxy.index(0, 0)).row()
                            self.assertIs(window.selected_element, window.record_model.record_at(source))
            finally:
                window.close()
                window.deleteLater()
                self.app.processEvents()


if __name__ == "__main__":
    unittest.main()
