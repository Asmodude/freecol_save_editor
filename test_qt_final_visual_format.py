"""Final Phase 1 visual polish: exact saved values remain unchanged."""
import unittest
from types import SimpleNamespace
from xml.etree.ElementTree import Element
from qt_final_visual_format import established_turn, colony_inspector_location
from qt_sorting import sort_key

class FinalVisualFormattingTests(unittest.TestCase):
    def test_established_turn_is_display_only(self):
        colony = Element('colony', {'established':'106'})
        self.assertEqual(established_turn(colony.get('established')), 'Turn 106')
        self.assertEqual(colony.get('established'), '106')
        self.assertEqual(established_turn(None), '')
        self.assertEqual(established_turn(''), '')

    def test_turn_column_keeps_numeric_sort_order(self):
        values = ['Turn 106','Turn 5','Turn 30']
        self.assertEqual(sorted(values, key=lambda v: sort_key(v, True)),
                         ['Turn 5','Turn 30','Turn 106'])

    def test_exact_tile_coordinates_only_in_inspector(self):
        colony = Element('colony', {'tile':'tile:321'})
        doc = SimpleNamespace(tiles={'tile:321': ('17','43')},
                              location_name=lambda tile: 'Christiansborg')
        self.assertEqual(colony_inspector_location(colony,doc),
                         'Christiansborg (17, 43)')
        self.assertEqual(doc.location_name(colony.get('tile')), 'Christiansborg')

    def test_missing_coordinates_do_not_get_invented(self):
        colony = Element('colony', {'tile':'tile:321'})
        doc = SimpleNamespace(tiles={}, location_name=lambda tile:'Christiansborg')
        self.assertEqual(colony_inspector_location(colony,doc),'Christiansborg')

if __name__ == '__main__':
    unittest.main()
