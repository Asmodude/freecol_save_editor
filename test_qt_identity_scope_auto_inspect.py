"""Identity-scoped tree entries immediately inspect their sole record."""
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication, QFileDialog
from qt_readonly import QtExplorer
from qt_navigation_lookup import find_navigation_item

_SAVE = b"""<?xml version="1.0"?><savedGame><game id="game:1" turn="10">
<player id="player:1" username="Human" nationId="model.nation.danish" playerType="colonial" ai="false" gold="100" tax="0"/>
<map width="4" height="4">
<tile id="tile:1" x="1" y="1" type="model.tile.plains" owner="player:1"><colony id="colony:1" name="Christiansborg" owner="player:1" tile="tile:1"/></tile>
<tile id="tile:2" x="2" y="2" type="model.tile.plains" owner="player:1"><colony id="colony:2" name="Taphus" owner="player:1" tile="tile:2"/></tile>
</map></game></savedGame>"""


class IdentityScopedAutoInspectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_specific_colony_auto_inspects_in_both_table_modes(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "single.fsg"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("savegame.xml", _SAVE)
            window = QtExplorer()
            try:
                with patch.object(QFileDialog, "getOpenFileName", return_value=(str(path), "")):
                    window.open_save()
                target = next(c for c in window.document.colonies if c.get("name") == "Christiansborg")
                scope = 'colony-id:' + target.get('id')
                item = find_navigation_item(window.navigation, 'Colonies', scope)
                self.assertIsNotNone(item)
                window.navigation.setCurrentItem(item)
                self.app.processEvents()
                self.assertIs(window.selected_element, target)
                self.assertIn("Christiansborg", window.inspector_label.text())
                window.set_model_view_comparison(True)
                self.app.processEvents()
                self.assertIs(window.selected_element, target)
                window.navigation.setCurrentItem(find_navigation_item(window.navigation, 'Colonies', 'mine'))
                self.app.processEvents()
                self.assertEqual(window.grid.rowCount(), 2)
                self.assertIsNone(window.selected_element)
            finally:
                window.close()


if __name__ == "__main__":
    unittest.main()
