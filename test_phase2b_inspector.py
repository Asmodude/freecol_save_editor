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

    def test_gold_editor_keeps_original_record_even_when_selection_changes(self):
        explorer = QtExplorer()
        try:
            player_a = Element("player", {"id": "player:1", "gold": "7225", "username": "A"})
            player_b = Element("player", {"id": "player:2", "gold": "100", "username": "B"})
            explorer.document = SimpleNamespace(players={"player:1": player_a, "player:2": player_b})
            explorer.group = "Players"
            explorer.update_gold_editor(player_a)
            self.assertEqual(explorer.gold_editor_key, ("player:1", "gold"))
            explorer.gold_edit.setText("9000")
            # A hypothetical focus/selection move must not change the captured target.
            explorer.selected_element = player_b
            with patch.object(explorer, "refresh_staged_view"):
                explorer.stage_selected_gold()
            self.assertEqual(explorer.session.edits, {("player:1", "gold"): (7225, 9000)})
            self.assertEqual(player_a.get("gold"), "7225")
            explorer.gold_edit.setText("9500")
            with patch.object(explorer, "refresh_staged_view"):
                explorer.stage_selected_gold()
            self.assertEqual(explorer.session.edits[("player:1", "gold")], (7225, 9500))
        finally:
            explorer.close()

    def test_native_gold_sentinel_does_not_offer_editor(self):
        explorer = QtExplorer()
        try:
            native = Element("player", {"id": "player:3", "gold": "-2147483648"})
            explorer.document = SimpleNamespace(players={"player:3": native})
            explorer.group = "Players"
            explorer.update_gold_editor(native)
            self.assertIsNone(explorer.gold_editor_key)
            self.assertFalse(explorer.gold_edit_widget.isVisible())
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
