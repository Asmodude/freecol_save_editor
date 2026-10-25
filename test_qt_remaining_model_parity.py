"""Read-only Qt model parity for native settlements and Founding Fathers."""
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

_SAVE = b"""<?xml version="1.0"?><savedGame><game id="game:1" turn="10">
<player id="player:1" username="Human" nationId="model.nation.danish" playerType="colonial" ai="false" gold="100" tax="0"/>
<player id="player:2" username="Native" nationId="model.nation.inca" playerType="indian" ai="true"/>
<map width="4" height="4"><tile id="tile:1" x="1" y="1" type="model.tile.plains" owner="player:2">
<indianSettlement id="settlement:1" name="Village One" owner="player:2" tile="tile:1"/>
</tile></map></game></savedGame>"""


class RemainingModelParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_native_settlement_and_father_columns_preserve_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "remaining.fsg"
            with zipfile.ZipFile(file, "w") as archive:
                archive.writestr("savegame.xml", _SAVE)
            window = QtExplorer()
            try:
                with patch.object(QFileDialog, "getOpenFileName", return_value=(str(file), "")):
                    window.open_save()
                for group, scope in (("Native settlements", "native"), ("Founding Fathers", "mine")):
                    with self.subTest(group=group):
                        target = find_navigation_item(window.navigation, group, scope)
                        self.assertIsNotNone(target)
                        window.navigation.setCurrentItem(target)
                        self.app.processEvents()
                        window.model_view.sortByColumn(0, Qt.SortOrder.DescendingOrder)
                        self.assertEqual(window.record_proxy.rowCount(), window.record_model.rowCount())
                        for visible_row in range(window.record_proxy.rowCount()):
                            source_row = window.record_proxy.mapToSource(window.record_proxy.index(visible_row, 0)).row()
                            self.assertIs(window.record_model.record_at(source_row), window.visible_rows[source_row])
                            for col in range(window.record_proxy.columnCount()):
                                self.assertEqual(window.record_proxy.data(window.record_proxy.index(visible_row, col)),
                                                 window.record_model.data(window.record_model.index(source_row, col)))
            finally:
                window.close()
                window.deleteLater()
                self.app.processEvents()


if __name__ == "__main__":
    unittest.main()
