"""Phase 2B B1 editor identity and pending-review behavioral tests."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from xml.etree.ElementTree import Element

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from edit_session import EditSession
from qt_staged_changes_panel import StagedChangesPanel
from qt_readonly import QtExplorer


class Phase2BInspectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_live_overview_editor_keeps_record_identity(self):
        explorer = QtExplorer()
        try:
            player_a = Element("player", {"id": "player:1", "gold": "7225", "username": "A"})
            player_b = Element("player", {"id": "player:2", "gold": "100", "username": "B"})
            explorer.document = SimpleNamespace(players={"player:1": player_a, "player:2": player_b})
            explorer.group = "Players"
            # The only production editor is the lower-middle Overview control.
            explorer.overview.setPlainText("Player A\nGold: 7225")
            explorer.overview.set_record("Players", player_a, explorer.document, explorer.session)
            from PySide6.QtWidgets import QLineEdit
            editor = explorer.overview.findChild(QLineEdit, "inlineGoldInput")
            self.assertIsNotNone(editor)
            self.assertFalse(hasattr(explorer, "gold_edit_widget"))
            explorer.selected_element = player_b
            editor.setText("9000")
            with patch.object(explorer, "refresh_staged_view"):
                editor.returnPressed.emit()
            self.assertEqual(explorer.session.edits, {("player:1", "gold"): (7225, 9000)})
            self.assertEqual(player_a.get("gold"), "7225")
            self.assertEqual(player_b.get("gold"), "100")
        finally:
            explorer.session.exported_snapshot = dict(explorer.session.edits)
            explorer.close()

    def test_native_sentinel_does_not_offer_live_overview_editor(self):
        explorer = QtExplorer()
        try:
            native = Element("player", {"id": "player:3", "gold": "-2147483648"})
            explorer.document = SimpleNamespace(players={"player:3": native})
            explorer.overview.setPlainText("Native\nGold: -2147483648")
            explorer.overview.set_record("Players", native, explorer.document, explorer.session)
            from PySide6.QtWidgets import QLineEdit
            self.assertIsNone(explorer.overview.findChild(QLineEdit, "inlineGoldInput"))
        finally:
            explorer.close()

    def test_panel_undo_resolves_item_key_not_visual_index(self):
        session = EditSession()
        session.stage(("player:1", "gold"), 100, 200)
        session.stage(("player:2", "tax"), 20, 25)
        panel = StagedChangesPanel(session)
        try:
            panel.tree.setSortingEnabled(True)
            panel.tree.sortItems(0, Qt.SortOrder.DescendingOrder)
            panel.tree.setCurrentItem(panel.tree.topLevelItem(0))
            chosen = panel.tree.topLevelItem(0).data(0, Qt.ItemDataRole.UserRole)
            panel.undo_selected()
            self.assertNotIn(chosen, session.edits)
            self.assertEqual(session.count, 1)
        finally:
            panel.close()


if __name__ == "__main__":
    unittest.main()
