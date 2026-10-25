"""Role-aware icon selection must distinguish a Veteran Dragoon from infantry."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication
from qt_unit_icons import UnitIcons


class RoleArtworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_dragoon_prefers_dragoon_directory_then_falls_back(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            infantry = root / "units" / "civilian"
            cavalry = root / "units" / "dragoon"
            infantry.mkdir(parents=True)
            cavalry.mkdir(parents=True)
            for path, color in ((infantry / "veteranSoldier.png", 0xff112233),
                                (cavalry / "veteranSoldier.png", 0xffaabbcc)):
                picture = QImage(3, 3, QImage.Format.Format_ARGB32)
                picture.fill(color)
                self.assertTrue(picture.save(str(path)))
            icons = UnitIcons(source=(root, None, "", None))
            normal = icons.icon("Veteran Soldier")
            dragoon = icons.icon("Veteran Soldier", role="model.role.dragoon")
            self.assertNotEqual(normal.pixmap(3, 3).toImage().pixel(0, 0),
                                dragoon.pixmap(3, 3).toImage().pixel(0, 0))
            self.assertIs(icons.icon("Veteran Soldier", role="model.role.dragoon"), dragoon)

    def test_unknown_role_keeps_existing_type_icon(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            location = root / "units" / "civilian"
            location.mkdir(parents=True)
            picture = QImage(3, 3, QImage.Format.Format_ARGB32)
            picture.fill(0xff778899)
            self.assertTrue(picture.save(str(location / "veteranSoldier.png")))
            icons = UnitIcons(source=(root, None, "", None))
            self.assertEqual(icons.icon("Veteran Soldier").pixmap(3, 3).toImage(),
                             icons.icon("Veteran Soldier", role="model.role.soldier").pixmap(3, 3).toImage())


if __name__ == "__main__":
    unittest.main()
