"""Phase 1 exit gate: protect accepted shell behavior and read-only boundaries.

Static checks supplement functional tests; Windows GUI acceptance remains mandatory.
"""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent

class Phase1ExitAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt=(ROOT/'qt_readonly.py').read_text(encoding='utf-8')
        cls.tree=ast.parse(cls.qt)
        cls.navigation=(ROOT/'qt_navigation_builder.py').read_text(encoding='utf-8')
        cls.search_ui=(ROOT/'qt_global_search_ui.py').read_text(encoding='utf-8')

    def test_read_only_shell_does_not_serialize_or_change_xml(self):
        forbidden=('.set(', '.append(', '.remove(', '.write(', 'produce(', '.save_as(')
        # Avoid naive string matching for Qt widget setters; test actual save entry points.
        self.assertNotIn('produce(',self.qt)
        self.assertNotIn('.save_as(',self.qt)
        self.assertNotIn('self.document.root.set(',self.qt)
        self.assertNotIn('self.document.game.set(',self.qt)
        self.assertIn('NoEditTriggers',self.qt)

    def test_scoped_nation_views_and_global_search_exist(self):
        for token in ("'National Goods'", "'Founding Fathers'", "'Game properties'",
                      "unit_group_scope(owner, 'vessel'", "('In the field', 'field')"):
            with self.subTest(token=token):
                self.assertIn(token,self.qt + self.navigation + self.search_ui)
        self.assertIn('self.global_button.clicked.connect(self.open_global_search)',self.qt)

    def test_sorted_navigation_uses_original_row_identity(self):
        self.assertIn('cell.setData(Qt.ItemDataRole.UserRole, row)',self.search_ui)
        self.assertIn('matches[source_index]',self.search_ui)
        self.assertIn('select_record_in_view(self.model_view, self.record_model, element)',self.search_ui)

    def test_development_only_override_removed(self):
        self.assertNotIn('C:\\\\Users\\\\morte', self.qt)
        self.assertNotIn('DEVELOPMENT ONLY: remove this local override', self.qt)
        self.assertIn("from qt_save_directory import save_directory", self.qt)
        self.assertIn("return save_directory(previous=self.art_settings.value(", self.qt)

    def test_phase1_entrypoint_compiles(self):
        compile(self.qt,'qt_readonly.py','exec')

if __name__=='__main__':
    unittest.main()
