"""FreeCol terminology and conservative Founding Father threshold calculations."""
import unittest
from types import SimpleNamespace
from xml.etree.ElementTree import fromstring
from qt_founding_father_progress import next_founding_father_cost
from qt_overview import record_overview


class FreeColTerminologyTests(unittest.TestCase):
    def test_founder_threshold_from_unambiguous_ruleset(self):
        root = fromstring('<savedGame><integerOption id="model.option.foundingFatherFactor" value="24"/></savedGame>')
        player = fromstring('<player id="player:1" liberty="14" immigration="18" immigrationRequired="89"/>')
        doc = SimpleNamespace(root=root, colony_counts={}, native_counts={})
        self.assertEqual(next_founding_father_cost(player, doc), 24)
        summary = record_overview('Players', player, doc)
        self.assertIn('Liberty Bells accumulated: 14', summary)
        self.assertIn('Liberty Bells needed to recruit next Founding Father: 24', summary)
        self.assertIn('Crosses accumulated: 18', summary)
        self.assertIn('Crosses needed for next immigrant to move to the docks in Europe: 89', summary)
        self.assertNotIn('Next immigrant progress', summary)

    def test_father_count_and_ambiguous_factor(self):
        player = fromstring('<player><foundingFathers x0="father1" x1="father2"/></player>')
        root = fromstring('<save><integerOption id="model.option.foundingFatherFactor" value="24"/></save>')
        self.assertEqual(next_founding_father_cost(player, SimpleNamespace(root=root)), 145)
        ambiguous = fromstring('<save><integerOption id="model.option.foundingFatherFactor" value="24"/>'
                               '<integerOption id="model.option.foundingFatherFactor" value="32"/></save>')
        self.assertIsNone(next_founding_father_cost(player, SimpleNamespace(root=ambiguous)))


if __name__ == '__main__':
    unittest.main()
