"""Portrait discovery uses existing FreeCol image files, never changes the archive."""
import tempfile
from pathlib import Path
from zipfile import ZipFile
import unittest
from qt_father_portraits import FatherPortraits, portrait_key


class FatherPortraitTests(unittest.TestCase):
    def test_safe_identifier_and_unavailable_fallback(self):
        self.assertEqual(portrait_key('model.foundingFather.simonBolivar'),'simonBolivar')
        self.assertIsNone(portrait_key('../evil'))
        with tempfile.TemporaryDirectory() as root:
            self.assertIsNone(FatherPortraits([root]).get('model.foundingFather.simonBolivar'))

    def test_read_local_and_archive(self):
        with tempfile.TemporaryDirectory() as root:
            folder=Path(root)/'data/default/resources/images/foundingFathers'
            folder.mkdir(parents=True)
            (folder/'simonBolivar.jpg').write_bytes(b'portrait')
            self.assertEqual(FatherPortraits([root]).get('model.foundingFather.simonBolivar'),b'portrait')
        with tempfile.TemporaryDirectory() as root:
            with ZipFile(Path(root)/'freecol.jar','w') as archive:
                archive.writestr('data/default/resources/images/foundingFathers/georgeWashington.jpg',b'jpeg')
            self.assertEqual(FatherPortraits([root]).get('model.foundingFather.georgeWashington'),b'jpeg')


if __name__=='__main__':
    unittest.main()
