"""Navigation artwork regression tests (run the Qt tests offscreen in CI)."""
import os
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
try:
    from PySide6.QtWidgets import QApplication
    from qt_navigation_icons import NavigationIcons, nation_key, EUROPEAN_FLAGS, flag_for_nation, NATIVE_STYLES, ICON_PALETTE
except ImportError:
    QApplication = None


@unittest.skipUnless(QApplication, 'PySide6 is required for graphical icon tests')
class NavigationArtworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.icons = NavigationIcons()

    def test_known_european_nations_have_non_null_flags(self):
        for identifier in ('model.nation.danish', 'model.nation.english',
                           'model.nation.french', 'model.nation.spanish',
                           'model.nation.dutch'):
            with self.subTest(identifier=identifier):
                icon = self.icons.icon('nation', identifier)
                self.assertFalse(icon.isNull())
                self.assertFalse(icon.pixmap(20, 20).isNull())

    def test_portugal_is_a_flag_not_a_local_square(self):
        icons = NavigationIcons()
        icons._source = (None, None, '', 'No assets')
        for alias in ('portuguese', 'portugal', 'model.nation.portuguese',
                      'model.nation.portugueseREF', 'model.nation.portugalREF'):
            with self.subTest(alias=alias):
                self.assertEqual(flag_for_nation(alias), 'portugal')
                for size in (20, 48):
                    with self.subTest(size=size):
                        pix = icons.icon('nation', alias, size=size).pixmap(size, size)
                        self.assertFalse(pix.isNull())
                        image = pix.toImage()
                        left = image.pixelColor(2, size // 2)
                        right = image.pixelColor(size - 3, size // 2)
                        self.assertGreater(left.green(), left.red() * 1.5)
                        self.assertGreater(right.red(), right.green() * 1.5)
                        self.assertNotEqual(left.name(), right.name())

    def test_portuguese_heraldry_contains_blue_escutcheons(self):
        icons = NavigationIcons()
        icons._source = (None, None, '', 'Unavailable')
        image = icons.icon('nation', 'model.nation.portuguese', size=96).pixmap(96, 96).toImage()
        blue_pixels = sum(
            1 for y in range(30, 68) for x in range(35, 62)
            if (lambda c: c.blue() > c.red() * 1.4 and c.blue() > c.green() * 1.2)(
                image.pixelColor(x, y)))
        self.assertGreater(blue_pixels, 8)

    def test_no_partial_nation_matching(self):
        self.assertIsNone(flag_for_nation('model.nation.portuguese_unknown'))
        self.assertIsNone(flag_for_nation('model.nation.portugueseREF_other'))

    def test_map_icon_is_blue_green_earth(self):
        icons = NavigationIcons()
        image = icons.icon('map', size=48).pixmap(48, 48).toImage()
        blue = green = 0
        for y in range(48):
            for x in range(48):
                pixel = image.pixelColor(x, y)
                if pixel.alpha() == 0:
                    continue
                if pixel.blue() > pixel.red() * 1.4:
                    blue += 1
                if pixel.green() > pixel.red() * 1.4:
                    green += 1
        self.assertGreater(blue, 100)
        self.assertGreater(green, 50)

    def test_every_navigation_kind_has_an_icon(self):
        for kind in ('overview', 'diplomacy', 'colonies', 'colony',
                     'units', 'ships', 'goods', 'research', 'fathers',
                     'options', 'map', 'section', 'settlements', 'nation'):
            with self.subTest(kind=kind):
                self.assertFalse(self.icons.icon(kind).isNull())

    def test_unknown_native_has_neutral_medallion(self):
        icon = self.icons.icon('nation', 'model.nation.unknowntribe', native=True)
        self.assertFalse(icon.isNull())

    def test_native_emblems_have_no_letter_substitution(self):
        for key in NATIVE_STYLES:
            with self.subTest(key=key):
                self.assertFalse(self.icons.icon('nation', 'model.nation.' + key, native=True).isNull())
        self.assertGreater(len(set(NATIVE_STYLES.values())), 4)

    def test_coloured_categories_have_distinct_palettes(self):
        self.assertNotEqual(ICON_PALETTE['colonies'], ICON_PALETTE['units'])
        self.assertNotEqual(ICON_PALETTE['goods'], ICON_PALETTE['research'])

    def test_missing_assets_still_render(self):
        icons = NavigationIcons()
        icons._source = (None, None, '', 'Unavailable')
        self.assertFalse(icons.icon('nation', 'model.nation.unknown').isNull())


class NationKeyTests(unittest.TestCase):
    def test_exact_identifier(self):
        self.assertEqual(nation_key('model.nation.danish'), 'danish')
        self.assertEqual(nation_key('model.nation.nativeSomething'), 'nativesomething')
        self.assertEqual(nation_key('../weird/path'), '')

    def test_explicit_mapping(self):
        self.assertEqual(EUROPEAN_FLAGS['danish'], 'denmark')
        self.assertEqual(EUROPEAN_FLAGS['portuguese'], 'portugal')
        self.assertEqual(EUROPEAN_FLAGS['portugal'], 'portugal')
        self.assertNotIn('aztec', EUROPEAN_FLAGS)


if __name__ == '__main__':
    unittest.main()
