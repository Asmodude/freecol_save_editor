"""Optional integration test against an actual FreeCol .fsg save.

Set FREECOL_TEST_SAVE to a privately held sample .fsg; never commit savegames.
Only a temporary destination is modified. No graphical display required.
"""
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

from edit_backend import produce


@unittest.skipUnless(os.environ.get("FREECOL_TEST_SAVE"), "Set FREECOL_TEST_SAVE to run real-save integration checks")
class RealSaveIntegrityTests(unittest.TestCase):
    def test_save_as_is_atomic_and_source_is_unchanged(self):
        source = Path(os.environ["FREECOL_TEST_SAVE"]).expanduser().resolve()
        self.assertTrue(source.is_file(), str(source))
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        with zipfile.ZipFile(source) as archive:
            xml = archive.read("savegame.xml")
            root = ET.fromstring(xml)
            players = [
                p for p in root.iter("player")
                if p.get("ai") == "false"
                and p.get("id", "").startswith("player:")
                and (p.get("gold") or "").isdigit()
                and 0 <= int(p.get("gold")) < 2147483647
            ]
            self.assertEqual(len(players), 1, "Expected exactly one human player with valid gold")
            player = players[0]
            owner, previous = player.get("id"), int(player.get("gold"))
            other_files = {n: archive.read(n) for n in archive.namelist() if n != "savegame.xml"}

        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "regression_output.fsg"
            edits = {(owner, "gold"): (previous, previous + 1)}
            result = produce(source, destination, edits)
            self.assertEqual(result["changes"], 1)
            self.assertTrue(destination.exists())
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)
            with zipfile.ZipFile(destination) as archive:
                self.assertIsNone(archive.testzip())
                outroot = ET.fromstring(archive.read("savegame.xml"))
                actual = [p.get("gold") for p in outroot.iter("player") if p.get("id") == owner]
                self.assertEqual(actual, [str(previous + 1)])
                self.assertEqual(
                    {n: archive.read(n) for n in archive.namelist() if n != "savegame.xml"},
                    other_files,
                )
            with self.assertRaises(ValueError):
                produce(source, source, edits)
            with self.assertRaises(FileExistsError):
                produce(source, destination, edits)
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)


if __name__ == "__main__":
    unittest.main()
