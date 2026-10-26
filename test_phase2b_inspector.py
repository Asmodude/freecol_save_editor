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
            explorer.document = SimpleNamespace(players={"player:1": player_a, "player:2": player_b}, xml_bytes=b'<save><game><player id="player:1" gold="7225"></player><player id="player:2" gold="100"></player></game></save>')
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

    def test_player_tax_uses_same_live_editor_and_backend_limits(self):
        explorer = QtExplorer()
        try:
            player = Element("player", {"id": "player:1", "gold": "7225", "tax": "20"})
            xml = b'<save><game><player id="player:1" gold="7225" tax="20"></player></game></save>'
            explorer.document = SimpleNamespace(players={"player:1": player}, xml_bytes=xml)
            explorer.group = "Players"
            explorer.overview.setPlainText("Player A\nGold: 7225\nTax: 20")
            explorer.overview.set_record("Players", player, explorer.document, explorer.session)
            from PySide6.QtWidgets import QLineEdit
            field = explorer.overview.findChild(QLineEdit, "inlineTaxInput")
            self.assertIsNotNone(field)
            field.setText("45")
            with patch.object(explorer, "refresh_staged_view"):
                field.returnPressed.emit()
            self.assertEqual(explorer.session.edits[("player:1", "tax")], (20, 45))
            self.assertEqual(player.get("tax"), "20")
        finally:
            explorer.session.exported_snapshot = dict(explorer.session.edits)
            explorer.close()

    def test_unit_experience_and_movement_inline_editors(self):
        explorer = QtExplorer()
        try:
            unit = Element("unit", {"id": "unit:1", "unitType": "model.unit.freeColonist",
                                  "owner": "player:1", "role": "model.role.default",
                                  "experience": "7", "movesLeft": "2"})
            xml = (b'<save><unit-type id="model.unit.freeColonist" movement="3"></unit-type>'
                   b'<role id="model.role.default"></role><game>'
                   b'<player id="player:1"></player>'
                   b'<unit id="unit:1" unitType="model.unit.freeColonist" '
                   b'owner="player:1" role="model.role.default" experience="7" movesLeft="2"></unit>'
                   b'</game></save>')
            explorer.document = SimpleNamespace(
                players={"player:1": Element("player", {"id": "player:1"})},
                unit_by_id=lambda uid: unit if uid == "unit:1" else None, xml_bytes=xml)
            explorer.group = "Units"
            explorer.overview.setPlainText("Unit One\\nExperience: 7\\nMoves left: 2")
            explorer.overview.set_record("Units", unit, explorer.document, explorer.session)
            from PySide6.QtWidgets import QLineEdit
            experience = explorer.overview.findChild(QLineEdit, "inlineExperienceInput")
            movement = explorer.overview.findChild(QLineEdit, "inlineMovesleftInput")
            self.assertIsNotNone(experience)
            self.assertIsNotNone(movement)
            with patch.object(explorer, "refresh_staged_view"):
                experience.setText("24")
                experience.returnPressed.emit()
                movement.setText("3")
                movement.returnPressed.emit()
            self.assertEqual(explorer.session.edits[("unit:1", "experience")], (7, 24))
            self.assertEqual(explorer.session.edits[("unit:1", "movesLeft")], (2, 3))
            self.assertEqual(unit.get("movesLeft"), "2")
            with patch("qt_readonly.QMessageBox.warning") as warning:
                explorer.stage_overview_edit("unit:1", "movesLeft", "4")
            warning.assert_called_once()
            self.assertEqual(explorer.session.edits[("unit:1", "movesLeft")], (2, 3))
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
