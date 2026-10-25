"""Portable save picker defaults, including remembered folders."""
import tempfile
import unittest
from pathlib import Path
from qt_save_directory import save_directory


class SaveDirectoryTests(unittest.TestCase):
    def test_prefers_last_used_existing_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            typical = home / 'Documents' / 'freecol' / 'save'
            typical.mkdir(parents=True)
            previous = home / 'Other Games'
            previous.mkdir()
            self.assertEqual(save_directory(home, previous), previous)

    def test_discovers_standard_and_onedrive_folders(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            target = home / 'OneDrive' / 'Dokumenter' / 'freecol' / 'save'
            target.mkdir(parents=True)
            self.assertEqual(save_directory(home), target)

    def test_nonexistent_preference_does_not_override_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            target = home / 'Documents' / 'FreeCol' / 'save'
            target.mkdir(parents=True)
            self.assertEqual(save_directory(home, home / 'missing'), target)

    def test_falls_back_to_home_when_no_candidates_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(save_directory(Path(tmp)), Path(tmp))


if __name__ == '__main__':
    unittest.main()
