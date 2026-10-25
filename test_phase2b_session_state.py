"""Phase 2B session lifecycle safety tests."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from edit_session import EditSession, EditValidationError


class ExportStateTests(unittest.TestCase):
    def test_original_cannot_change_when_restaging(self):
        session = EditSession()
        key = ("player:19", "gold")
        session.stage(key, 7225, 8000)
        session.stage(key, 7225, 9000)
        self.assertEqual(session.edits[key], (7225, 9000))
        with self.assertRaises(EditValidationError):
            session.stage(key, 8000, 9500)
        self.assertEqual(session.edits[key], (7225, 9000))
        session.unstage(key)
        self.assertEqual(session.count, 0)

    def test_successful_export_marks_snapshot_clean_but_keeps_edits(self):
        session = EditSession()
        key = ("player:19", "gold")
        session.stage(key, 7225, 9000)
        self.assertTrue(session.has_unexported_changes)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "original.fsg"
            destination = Path(directory) / "exported.fsg"
            source.write_bytes(b"fixture")
            with patch("edit_session.produce", return_value="exported") as producer:
                self.assertEqual(session.save_as(source, destination), "exported")
                producer.assert_called_once()
            self.assertEqual(session.exported_path, destination)
            self.assertFalse(session.has_unexported_changes)
            self.assertEqual(session.edits[key], (7225, 9000))
            session.stage(key, 7225, 9500)
            self.assertTrue(session.has_unexported_changes)
            session.stage(key, 7225, 9000)
            self.assertFalse(session.has_unexported_changes)
            session.unstage(key)
            self.assertTrue(session.has_unexported_changes)

    def test_failed_export_does_not_mark_changes_clean(self):
        session = EditSession()
        session.stage(("player:19", "gold"), 7225, 9000)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "original.fsg"
            destination = Path(directory) / "exported.fsg"
            source.write_bytes(b"fixture")
            with patch("edit_session.produce", side_effect=ValueError("invalid XML")):
                with self.assertRaisesRegex(ValueError, "invalid XML"):
                    session.save_as(source, destination)
        self.assertTrue(session.has_unexported_changes)
        self.assertEqual(session.exported_snapshot, {})
        self.assertIsNone(session.exported_path)


if __name__ == "__main__":
    unittest.main()
