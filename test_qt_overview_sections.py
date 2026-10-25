"""Behavioral regression: colony Overview headings must contain their data."""
import unittest
from qt_overview_sections import overview_sections

class OverviewGroupingTests(unittest.TestCase):
    SAMPLE = (
        'Christiansborg\n\nOwner: Danish\nEstablished: 5\n'
        'Population and activity\nWorkers: 6\nBuildings: 14\n'
        'Largest warehouse stockpiles\nBells: 649\nOre: 306\n'
        '…and 9 more goods types\n'
        'Occupied buildings\nTown Hall: 1 worker\n'
        'Select Buildings, Workers, Stationed units or Goods for item-level details.'
    )

    def test_headings_keep_their_own_values(self):
        name, sections = overview_sections(self.SAMPLE)
        self.assertEqual(name, 'Christiansborg')
        self.assertEqual([s[0] for s in sections],
                         ['Colony properties', 'Population and activity',
                          'Largest warehouse stockpiles', 'Occupied buildings'])
        self.assertIn(('Bells','649'), sections[2][1])
        self.assertIn(('Town Hall','1 worker'), sections[3][1])
        self.assertNotIn(('Bells','649'), sections[0][1])
        self.assertEqual(sections[2][2], ['…and 9 more goods types'])

    def test_without_stockpiles_does_not_invent_them(self):
        _, sections = overview_sections('Empty\nOwner: Danish\nPopulation and activity\nWorkers: 0')
        self.assertEqual(len(sections),2)
        self.assertEqual(sections[1][1],[('Workers','0')])

    def test_empty_text(self):
        self.assertEqual(overview_sections(''), ('', []))

if __name__ == '__main__':
    unittest.main()
