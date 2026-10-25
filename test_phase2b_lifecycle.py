"""Qt dirty-state and safe Save As behavior for Phase 2B."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog
from qt_readonly import QtExplorer


class Phase2BLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = QtExplorer()
        self.window.session.stage(("player:1", "gold"), 10, 20)

    def tearDown(self):
        self.window.session.exported_snapshot = dict(self.window.session.edits)
        self.window.close()

    def test_cancel_discards_nothing(self):
        with patch("qt_readonly.QMessageBox.question", return_value=QMessageBox.StandardButton.Cancel):
            self.assertFalse(self.window.confirm_discard())
        self.assertEqual(self.window.session.count, 1)

    def test_exported_state_requires_no_discard_prompt(self):
        self.window.session.exported_snapshot = dict(self.window.session.edits)
        with patch("qt_readonly.QMessageBox.question") as prompt:
            self.assertTrue(self.window.confirm_discard())
            prompt.assert_not_called()

    def test_undo_after_export_is_dirty_even_when_count_zero(self):
        self.window.session.exported_snapshot = dict(self.window.session.edits)
        self.window.session.exported_path = Path('last_export.fsg')
        self.window.session.unstage(("player:1", "gold"))
        self.assertEqual(self.window.session.count, 0)
        self.assertTrue(self.window.session.has_unexported_changes)
        with patch("qt_readonly.QMessageBox.question",
                   return_value=QMessageBox.StandardButton.Cancel) as prompt:
            self.assertFalse(self.window.confirm_discard())
            self.assertIn("0 currently staged changes", prompt.call_args.args[2])
        self.window.update_save_button()
        self.assertFalse(self.window.save_button.isEnabled())

    def test_save_as_uses_safe_dialog_and_original_source(self):
        with tempfile.TemporaryDirectory() as folder:
            original = Path(folder) / "test.fsg"
            original.write_bytes(b"original")
            self.window.document = SimpleNamespace(path=original)
            dest = str(Path(folder) / "test_edited.fsg")
            with patch("qt_readonly.QFileDialog.getSaveFileName", return_value=(dest, "")) as dialog:
                with patch.object(self.window.session, "save_as") as export:
                    with patch("qt_readonly.QMessageBox.information"):
                        self.window.save_as()
                dialog.assert_called_once()
                self.assertEqual(dialog.call_args.kwargs["options"], QFileDialog.Option.DontConfirmOverwrite)
                export.assert_called_once_with(original, dest)
            self.assertEqual(original.read_bytes(), b"original")

    def test_existing_save_export_failure_retains_pending_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            original = Path(folder) / "test.fsg"
            original.write_bytes(b"original")
            self.window.document = SimpleNamespace(path=original)
            with patch("qt_readonly.QFileDialog.getSaveFileName", return_value=(str(original), "")):
                with patch("qt_readonly.QMessageBox.warning") as warning:
                    self.window.save_as()
            warning.assert_called_once()
            self.assertEqual(self.window.session.count, 1)
            self.assertTrue(self.window.session.has_unexported_changes)
            self.assertEqual(original.read_bytes(), b"original")


if __name__ == "__main__":
    unittest.main()
