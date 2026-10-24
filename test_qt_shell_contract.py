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

    def test_load_batches_navigation_and_supports_diagnostics(self):
        self.assertIn('self.navigation.setUpdatesEnabled(False)', self.source)
        self.assertIn('self.navigation.setUpdatesEnabled(True)', self.source)
        self.assertIn('FREECOL_QT_PROFILE', self.source)
        self.assertIn('icons = {kind: self.style().standardIcon(icon)', self.source)

    def test_navigation_styles_preserve_semantic_filters(self):
        self.assertIn("self.navigation.setIndentation(19)", self.source)
        self.assertIn("kind='nation'", self.source)
        self.assertIn("kind='colony'", self.source)
        self.assertIn("item.setData(0, Qt.ItemDataRole.UserRole, (group, scope))", self.source)
        self.assertIn("item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)", self.source)

    def test_detail_unit_navigation_is_read_only(self):
        self.assertIn("self.jump_unit_button.clicked.connect(self.open_detail_unit)", self.source)
        self.assertIn("self.document.unit_by_id(unit_id)", self.source)
        self.assertIn("self.grid.selectRow(display_row_index)", self.source)
        self.assertNotIn('self.document.save(', self.source)

    def test_global_search_sort_preserves_record_identity(self):
        self.assertIn('results.setSortingEnabled(True)', self.source)
        self.assertIn('results.setSortingEnabled(False)', self.source)
        self.assertIn('cell.setData(Qt.ItemDataRole.UserRole, row)', self.source)
        self.assertIn('matches[source_index]', self.source)

    def test_separate_workspace_and_inspector(self):
        self.assertIn('self.overview = QPlainTextEdit()', self.source)
        self.assertIn('self.details = QPlainTextEdit()', self.source)
        self.assertIn('self.grid.itemSelectionChanged.connect(self.inspect)', self.source)


if __name__ == '__main__':
    unittest.main()
