"""Phase 1 Qt module static checks that do not require PySide6 on CI."""
import ast
import unittest
from pathlib import Path


class QtShellContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (Path(__file__).resolve().parent / 'qt_readonly.py').read_text(encoding='utf-8')
        cls.tree = ast.parse(cls.source)

    def test_read_only_entry_point_and_no_save_mutation(self):
        self.assertIn('SaveDocument.load(', self.source)
        self.assertNotIn('produce(', self.source)
        self.assertNotIn('.save_as(', self.source)
        self.assertIn('NoEditTriggers', self.source)

    def test_map_editor_entry_point_is_honest(self):
        self.assertIn("QPushButton('Open Map Editor')", self.source)
        self.assertIn('self.map_button.setEnabled(False)', self.source)
        self.assertIn('available in the Tkinter application', self.source)

    def test_separate_workspace_and_inspector(self):
        self.assertIn('self.overview = QPlainTextEdit()', self.source)
        self.assertIn('self.details = QPlainTextEdit()', self.source)
        self.assertIn('self.grid.itemSelectionChanged.connect(self.inspect)', self.source)


if __name__ == '__main__':
    unittest.main()
