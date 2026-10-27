"""Phase 2D-1: shared staging control and permanent source clarification."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import unittest

from PySide6.QtWidgets import QApplication, QPushButton
from qt_stage_controls import StageChangeButton, style_stage_choice
from PySide6.QtWidgets import QComboBox
from qt_staged_changes_panel import StagedChangesPanel
from edit_session import EditSession
from qt_readonly import QtExplorer


class Phase2DUxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_shared_control_accessible_and_clickable(self):
        button = StageChangeButton()
        clicks = []
        button.clicked.connect(lambda: clicks.append(True))
        self.assertIsInstance(button, QPushButton)
        self.assertEqual(button.text(), "Stage Change")
        self.assertEqual(button.accessibleName(), "Stage Change")
        self.assertGreaterEqual(button.minimumWidth(), button.sizeHint().width())
        button.click()
        self.assertEqual(clicks, [True])
        button.deleteLater()

    def test_choice_styling_identifies_editable_and_staged(self):
        combo = QComboBox()
        style_stage_choice(combo, False)
        self.assertIn('#76A9E8', combo.styleSheet())
        style_stage_choice(combo, True)
        self.assertIn('#26815A', combo.styleSheet())
        combo.deleteLater()

    def test_pioneer_staged_change_explains_tools_and_rolecount(self):
        panel = StagedChangesPanel(EditSession())
        try:
            values = panel.labels_for(('unit:5', 'equipment'),
                ('model.role.default', 0), ('model.role.pioneer', 4))
            self.assertIn('80 tools', values[3])
            self.assertIn('roleCount: 4', values[3])
        finally:
            panel.deleteLater()

    def test_instructions_and_source_notice_are_permanent(self):
        window = QtExplorer()
        try:
            self.assertIn('Edit data one at a time', window.editing_instructions.text())
            self.assertIn('Stage Change', window.editing_instructions.text())
            self.assertIn('excluding staged changes', window.inspector_source_notice.text())
            self.assertIn('roleCount=0', window.inspector_source_notice.text())
            self.assertEqual(window.inspector_tabs.tabText(0), 'Details (source)')
            self.assertEqual(window.inspector_tabs.tabText(1), 'Raw XML (source)')
        finally:
            window.close()
            window.deleteLater()


if __name__ == "__main__":
    unittest.main()
