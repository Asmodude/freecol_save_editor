"""Phase 2D-1: shared staging control and permanent source clarification."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import unittest

from PySide6.QtWidgets import QApplication, QPushButton
from qt_stage_controls import StageChangeButton
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
