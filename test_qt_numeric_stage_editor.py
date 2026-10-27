"""Offscreen behavioural contract for the shared numeric stage editor."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
from PySide6.QtWidgets import QApplication
from qt_numeric_stage_editor import NumericStageEditor


class NumericStageEditorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_pending_typing_is_not_staged_until_explicit_action(self):
        editor = NumericStageEditor(12, 8, staged=True, object_name='testAmount')
        seen = []
        editor.stage_requested.connect(seen.append)
        self.assertEqual(editor.original_label.text(), 'was 8')
        editor.edit.setText('19')
        self.assertEqual(seen, [])
        self.assertEqual(editor.status.text(), 'Not staged')
        self.assertFalse(editor.status.isHidden() is False and editor.status.text() == '')
        editor.edit.returnPressed.emit()
        self.assertEqual(seen, ['19'])
        editor.edit.setText('20')
        editor.button.click()
        self.assertEqual(seen, ['19', '20'])
        editor.edit.setText('12')
        self.assertEqual(editor.status.text(), '')
        self.assertEqual(editor.edit.objectName(), 'testAmount')

    def test_unstaged_has_no_original_label_and_blue_border(self):
        editor = NumericStageEditor(30, 30, staged=False)
        self.assertIsNone(editor.original_label)
        self.assertIn('#76A9E8', editor.edit.styleSheet())
        self.assertEqual(editor.button.text(), 'Stage Change')

    def test_staged_uses_existing_green_convention(self):
        editor = NumericStageEditor(31, 30, staged=True)
        self.assertIn('#26815A', editor.edit.styleSheet())


if __name__ == '__main__':
    unittest.main()
