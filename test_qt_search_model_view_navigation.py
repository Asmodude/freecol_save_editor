"""Global search navigation must target the active QTableView by record identity."""
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication, QFileDialog
from qt_readonly import QtExplorer
from qt_record_table_view import selected_source_record

_SAVE = b"""<?xml version="1.0"?><savedGame><game id="game:1" turn="10">
<player id="player:1" username="Human" nationId="model.nation.danish" playerType="colonial" ai="false" gold="100" tax="0"/>
<map width="4" height="4">
<tile id="tile:1" x="1" y="1" type="model.tile.plains" owner="player:1"><colony id="colony:1" name="Zulu" owner="player:1" tile="tile:1"/></tile>
<tile id="tile:2" x="2" y="2" type="model.tile.plains" owner="player:1"><colony id="colony:2" name="Alpha" owner="player:1" tile="tile:2"/></tile>
</map></game></savedGame>"""


class SearchToViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_global_navigation_selects_exact_colony_in_comparison_mode(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "global.fsg"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("savegame.xml", _SAVE)
            window = QtExplorer()
            try:
                with patch.object(QFileDialog, "getOpenFileName", return_value=(str(path), "")):
                    window.open_save()
                for colony in window.document.colonies:
                    with self.subTest(colony=colony.get("name")):
                        window.navigate_to_global_result("Colonies", colony)
                        self.app.processEvents()
                        self.assertIs(selected_source_record(window.model_view, window.record_model), colony)
                        self.assertIs(window.selected_element, colony)
            finally:
                window.close()
                window.deleteLater()
                self.app.processEvents()


if __name__ == "__main__":
    unittest.main()
