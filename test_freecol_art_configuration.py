"""Portable, validated artwork folder selection: no Qt or game installation required."""
import tempfile
import unittest
from pathlib import Path
from freecol_art_source import (
    discover, validate_installation, set_installation_root, configured_root,
)

class FreeColArtConfigurationTests(unittest.TestCase):
    def tearDown(self):
        set_installation_root(None)

    def test_valid_nonstandard_installation(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            art=root/'data'/'default'/'resources'/'images'/'units'/'civilian'
            art.mkdir(parents=True)
            (art/'freeColonist.png').write_bytes(b'fake-art')
            valid,status=validate_installation(root)
            self.assertTrue(valid,status)
            set_installation_root(root)
            base,archive,prefix,_=discover()
            self.assertEqual(base,art.parent.parent)
            self.assertIsNone(archive)

    def test_bad_directory_rejected_without_overriding_previous(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            valid,_=validate_installation(root)
            self.assertFalse(valid)
            self.assertIsNone(configured_root())

    def test_auto_mode_restored(self):
        set_installation_root(Path('/not-a-real-game'))
        self.assertIsNotNone(configured_root())
        set_installation_root(None)
        self.assertIsNone(configured_root())

if __name__ == '__main__':
    unittest.main()
