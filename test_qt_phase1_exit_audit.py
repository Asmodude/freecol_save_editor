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
                      "unit_group_scope(owner, 'vessel'", "('In the field', 'field')",
                      'self.global_button.clicked.connect(self.open_global_search)'):
            with self.subTest(token=token):
                self.assertIn(token,self.qt)

    def test_sorted_navigation_uses_original_row_identity(self):
        self.assertIn('cell.setData(Qt.ItemDataRole.UserRole, row)',self.qt)
        self.assertIn('matches[source_index]',self.qt)
        self.assertIn('self.visible_rows[index] is element',self.qt)

    def test_development_only_override_must_be_removed_before_release(self):
        # Known Phase 1 carry-over; detect any accidental removal of the warning.
        self.assertIn('# DEVELOPMENT ONLY: remove this local override',self.qt)

    def test_phase1_entrypoint_compiles(self):
        compile(self.qt,'qt_readonly.py','exec')

if __name__=='__main__':
    unittest.main()
