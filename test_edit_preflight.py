"""C1 backend preflight: source immutable and invalid candidate never staged."""
import unittest
from edit_session import EditSession
from edit_preflight import preflight, stage_checked, unstage_checked

XML = b'<save><game><player id="player:1" gold="100" tax="20"></player><player id="player:2" gold="50" tax="10"></player></game></save>'

class PreflightTests(unittest.TestCase):
    def test_combined_valid_stage_matches_source_and_preserves_xml(self):
        session = EditSession()
        stage_checked(session, XML, ("player:1", "gold"), 100, 125)
        stage_checked(session, XML, ("player:1", "tax"), 20, 25)
        self.assertEqual(XML.count(b'gold="100"'), 1)
        self.assertEqual(session.count, 2)
        output = preflight(XML, session.edits)
        self.assertIn(b'gold="125"', output)
        self.assertIn(b'tax="25"', output)
        self.assertIn(b'gold="50"', output)

    def test_backend_rejection_keeps_session_unchanged(self):
        session = EditSession()
        stage_checked(session, XML, ("player:1", "gold"), 100, 125)
        before = dict(session.edits)
        with self.assertRaisesRegex(ValueError, "out of range"):
            stage_checked(session, XML, ("player:1", "tax"), 20, 120)
        self.assertEqual(session.edits, before)

    def test_bad_source_original_cannot_be_staged(self):
        session = EditSession()
        with self.assertRaisesRegex(ValueError, "Stale value"):
            stage_checked(session, XML, ("player:1", "gold"), 99, 125)
        self.assertEqual(session.count, 0)

    def test_safe_undo_repreflights_remaining_changes(self):
        session = EditSession()
        stage_checked(session, XML, ("player:1", "gold"), 100, 125)
        stage_checked(session, XML, ("player:1", "tax"), 20, 25)
        unstage_checked(session, XML, ("player:1", "gold"))
        self.assertEqual(session.count, 1)
        self.assertIn(b'tax="25"', preflight(XML, session.edits))

if __name__ == "__main__":
    unittest.main()
