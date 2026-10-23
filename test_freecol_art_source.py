"""Headless FreeCol art discovery and bytes regression."""
import tempfile
import unittest
import zipfile
from pathlib import Path
from freecol_art_source import discover,read_bytes


class ArtworkSourceTests(unittest.TestCase):
    def test_directory_source_and_missing_asset(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            base=root/'resources'/'images'
            (base/'terrain').mkdir(parents=True)
            (base/'terrain'/'sample.png').write_bytes(b'fixture')
            directory,archive,prefix,status=discover([root])
            self.assertEqual(directory,base)
            self.assertIsNone(archive)
            self.assertEqual(prefix,'')
            self.assertIn('FreeCol graphics:',status)
            self.assertEqual(read_bytes(directory,archive,prefix,'terrain/sample.png'),b'fixture')
            self.assertIsNone(read_bytes(directory,archive,prefix,'missing.png'))

    def test_zip_source_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            arc=root/'freecol.jar'
            with zipfile.ZipFile(arc,'w') as z:
                z.writestr('data/default/resources/images/terrain/savannah/center0.size9.png',b'anchor')
                z.writestr('data/default/resources/images/terrain/river/center0.png',b'water')
            directory,archive,prefix,status=discover([root])
            self.assertIsNone(directory)
            self.assertEqual(archive,arc)
            self.assertEqual(prefix,'data/default/resources/images/')
            self.assertEqual(read_bytes(directory,archive,prefix,'terrain/river/center0.png'),b'water')
            self.assertIsNone(read_bytes(directory,archive,prefix,'terrain/absent.png'))

    def test_absent_installation_falls_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'nonexistent'
            base,archive,prefix,status=discover([root])
            self.assertIsNone(base)
            self.assertIsNone(archive)
            self.assertIn('not found',status)
            self.assertIsNone(read_bytes(base,archive,prefix,'terrain/test.png'))


if __name__=='__main__':
    unittest.main()
