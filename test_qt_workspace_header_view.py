"""Offscreen tests for extracted Qt workspace header presentation."""
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication
from qt_readonly import QtExplorer
from qt_workspace_header_view import WorkspaceHeaderMixin


class WorkspaceHeaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_header_updates_with_current_group(self):
        window = QtExplorer()
        try:
            self.assertIsInstance(window, WorkspaceHeaderMixin)
            window.group = "Game properties"
            window.scope = "game"
            window.update_workspace_header()
            self.assertTrue(window.workspace_title.text())
            self.assertTrue(window.search.placeholderText())
            window.group = "Players"
            window.scope = "mine"
            window.update_workspace_header()
            self.assertTrue(window.workspace_title.text())
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
