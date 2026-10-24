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
        for alias in ('portuguese', 'portugal', 'model.nation.portuguese'):
            with self.subTest(alias=alias):
                self.assertEqual(flag_for_nation(alias), 'portugal')
                pix = icons.icon('nation', alias).pixmap(20, 20)
                self.assertFalse(pix.isNull())
                # Both the green and red portions must be visibly present.
                self.assertGreater(pix.toImage().pixelColor(2, 10).green(), 40)
                self.assertGreater(pix.toImage().pixelColor(17, 10).red(), 150)

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
