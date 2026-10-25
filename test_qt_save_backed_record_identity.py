"""Offscreen integration: real save archive, sorted selection and Qt model identity.

Every selected legacy table row must resolve to the same XML object mirrored by
RecordTableModel, including after resorting and changing the search filter.
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

from qt_readonly import QtExplorer


_SAVE = b"""<?xml version="1.0"?><savedGame><game id="game:1" turn="10">
<player id="player:1" username="Human" nationId="model.nation.danish" playerType="colonial" ai="false" gold="100" tax="0"/>
<map width="4" height="4">
<tile id="tile:1" x="1" y="1" type="model.tile.plains" owner="player:1">
 <colony id="colony:1" name="Zulu" owner="player:1" tile="tile:1"/>
</tile>
<tile id="tile:2" x="2" y="2" type="model.tile.plains" owner="player:1">
 <colony id="colony:2" name="Alpha" owner="player:1" tile="tile:2"/>
</tile>
</map></game></savedGame>"""


class SaveBackedRecordIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "identity.fsg"
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
        self.tmp.cleanup()

    def test_single_human_player_is_selected_without_click(self):
        w = self.window
        self.assertEqual(w.group, 'Players')
        self.assertEqual(w.record_model.rowCount(), 1)
        self.assertIs(w.selected_element, w.record_model.record_at(0))
        self.assertIn('Human', w.inspector_label.text())
        self.assertIsNotNone(w.overview.findChild(
            __import__('PySide6.QtWidgets', fromlist=['QLineEdit']).QLineEdit,
            'inlineGoldInput'))

    def test_sorted_colonies_select_correct_xml_record(self):
        from qt_navigation_lookup import find_navigation_item
        w = self.window
        item = find_navigation_item(w.navigation, "Colonies", "mine")
        self.assertIsNotNone(item)
        w.navigation.setCurrentItem(item)
        self.app.processEvents()
        self.assertEqual(w.record_proxy.rowCount(), 2)
        self.assertEqual(w.record_model.rowCount(), 2)
        w.model_view.sortByColumn(1, Qt.SortOrder.DescendingOrder)  # Name
        for display_row in range(w.record_proxy.rowCount()):
            source_row = w.record_proxy.mapToSource(w.record_proxy.index(display_row, 0)).row()
            expected = w.record_model.record_at(source_row)
            w.model_view.setCurrentIndex(w.record_proxy.index(display_row, 0))
            self.app.processEvents()
            self.assertIs(w.selected_element, expected)

    def test_filter_rebuilds_model_and_selection_identity(self):
        from qt_navigation_lookup import find_navigation_item
        w = self.window
        w.navigation.setCurrentItem(find_navigation_item(w.navigation, "Colonies", "mine"))
        w.search.setText("Alpha")
        self.app.processEvents()
        self.assertEqual(w.record_proxy.rowCount(), 1)
        self.assertEqual(w.record_model.rowCount(), 1)
        self.assertEqual(w.record_model.record_at(0).get("name"), "Alpha")
        # A filtered singleton is automatically inspected without a second click.
        self.assertIs(w.selected_element, w.record_model.record_at(0))
        self.assertEqual(w.inspector_label.text(), 'Alpha')


if __name__ == "__main__":
    unittest.main()
