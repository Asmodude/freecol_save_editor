"""Offscreen behavioral regression tests for Phase 2B staged-change controls."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import unittest
from PySide6.QtWidgets import QApplication
from edit_session import EditSession
from qt_staged_changes_panel import StagedChangesPanel


class StagedChangesPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.session = EditSession()
        self.panel = StagedChangesPanel(self.session)

    def tearDown(self):
        self.panel.close()

    def test_empty_session_disables_actions(self):
        self.assertEqual(self.panel.tree.topLevelItemCount(), 0)
        self.assertFalse(self.panel.undo_button.isEnabled())
        self.assertFalse(self.panel.clear_button.isEnabled())
        self.assertEqual(self.panel.heading.text(), "Pending changes: 0")

    def test_refresh_displays_staged_changes_without_mutating_source(self):
        original = ("player:1", "gold")
        self.session.stage(original, 100, 150)
        self.panel.refresh()
        self.assertEqual(self.panel.tree.topLevelItemCount(), 1)
        self.assertEqual(self.panel.tree.topLevelItem(0).text(2), "100")
        self.assertEqual(self.panel.tree.topLevelItem(0).text(3), "150")
        self.assertEqual(self.session.edits[original], (100, 150))
        self.assertEqual(self.panel.heading.text(), "Pending changes: 1")

    def test_undo_selected_preserves_other_edits_and_emits_signal(self):
        a = ("player:1", "gold")
        b = ("player:1", "tax")
        self.session.stage(a, 100, 150)
        self.session.stage(b, 30, 40)
        self.panel.refresh()
        observed = []
        self.panel.changed.connect(lambda: observed.append(self.session.count))
        self.panel.tree.setCurrentItem(self.panel.tree.topLevelItem(0))
        self.panel.undo_selected()
        self.assertEqual(self.session.edits, {b: (30, 40)})
        self.assertEqual(observed, [1])
        self.assertEqual(self.panel.tree.topLevelItemCount(), 1)

    def test_unstage_all_clears_session_and_emits_signal(self):
        self.session.stage(("player:1", "gold"), 1, 2)
        self.session.stage(("player:1", "tax"), 3, 4)
        self.panel.refresh()
        observed = []
        self.panel.changed.connect(lambda: observed.append(True))
        self.panel.unstage_all()
        self.assertFalse(self.session.edits)
        self.assertEqual(self.panel.heading.text(), "Pending changes: 0")
        self.assertEqual(observed, [True])


if __name__ == "__main__":
    unittest.main()
