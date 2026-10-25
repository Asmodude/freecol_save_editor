"""Offscreen regression checks for locally sourced FreeCol unit artwork."""
import os
import tempfile
import unittest
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

try:
    from PySide6.QtGui import QColor, QPixmap
    from PySide6.QtWidgets import QApplication
    from qt_unit_icons import UnitIcons, unit_key
    from qt_property_icons import property_icon
except ImportError:
    QApplication = None


@unittest.skipUnless(QApplication is not None, 'PySide6 required')
class UnitIconTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_unit_type_keys(self):
        self.assertEqual(unit_key('model.unit.freeColonist'), 'freeColonist')
        self.assertEqual(unit_key('Free Colonist'), 'freeColonist')
        self.assertEqual(unit_key('Expert Farmer'), 'expertFarmer')

    def test_local_png_is_used_in_preference_to_fallback(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder/'units').mkdir()
            sprite = QPixmap(24, 24)
            sprite.fill(QColor('#14a26b'))
            self.assertTrue(sprite.save(str(folder/'units'/'freeColonist.png')))
            icons = UnitIcons(source=(folder, None, '', 'test'))
            pix = icons.icon('model.unit.freeColonist', 24).pixmap(24, 24)
            self.assertEqual(pix.toImage().pixelColor(12, 12).name(), '#14a26b')

    def test_nested_civilian_sprite_is_selected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder/'units'/'civilian').mkdir(parents=True)
            sprite = QPixmap(24, 24)
            sprite.fill(QColor('#17c38a'))
            self.assertTrue(sprite.save(str(folder/'units'/'civilian'/'freeColonist.png')))
            icon = UnitIcons(source=(folder, None, '', 'test')).icon(
                'model.unit.freeColonist', 24)
            self.assertEqual(icon.pixmap(24,24).toImage().pixelColor(12,12).name(), '#17c38a')

    def test_missing_assets_are_visible_without_cross(self):
        icons = UnitIcons(source=(None, None, '', 'unavailable'))
        pix = icons.icon('model.unit.freeColonist', 24).pixmap(24, 24)
        self.assertFalse(pix.isNull())
        self.assertGreater(pix.toImage().pixelColor(12, 12).alpha(), 0)

    def test_location_pin_renders_red_tip_and_white_centre(self):
        im = property_icon('Location', 32).pixmap(32, 32).toImage()
        self.assertGreater(im.pixelColor(16, 25).red(), 140)
        self.assertGreater(im.pixelColor(16, 12).red(), 180)

if __name__ == '__main__':
    unittest.main()
