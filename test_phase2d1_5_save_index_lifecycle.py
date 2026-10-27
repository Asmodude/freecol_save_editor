"""Phase 2D-1.5: document-scoped lazy cache and benchmark smoke tests."""
import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace
from save_document import SaveDocument
from benchmark_phase2d1_5 import sample_units


class LazyCacheTests(unittest.TestCase):
    def test_cache_is_lazy_reused_and_not_shared_across_saves(self):
        first = SaveDocument()
        first.root = ET.fromstring('<save><role id="model.role.pioneer"/></save>')
        first._equipment_rules_index = None
        second = SaveDocument()
        second.root = ET.fromstring('<save><role id="model.role.soldier"/></save>')
        second._equipment_rules_index = None
        self.assertIsNone(first._equipment_rules_index)
        index = first.equipment_rules_index
        self.assertIs(index, first.equipment_rules_index)
        self.assertIn('model.role.pioneer', index.roles)
        self.assertNotIn('model.role.soldier', index.roles)
        second_index = second.equipment_rules_index
        self.assertIsNot(index, second_index)
        self.assertIn('model.role.soldier', second_index.roles)
        self.assertNotIn('model.role.pioneer', second_index.roles)
        with self.assertRaises(TypeError):
            index.roles['model.role.forbidden'] = ()

    def test_benchmark_repeats_only_authoritative_units(self):
        units = [
            ET.Element('unit', {'id': 'unit:1',
                'owner': 'player:1', 'unitType': 'model.unit.freeColonist'}),
            ET.Element('unit', {'id': 'unit:2',
                'owner': 'player:missing', 'unitType': 'model.unit.freeColonist'}),
        ]
        document = SimpleNamespace(units=units, players={'player:1':object()})
        chosen = sample_units(document, 15)
        self.assertEqual(len(chosen), 15)
        self.assertTrue(all(unit.get('id') == 'unit:1' for unit in chosen))


if __name__ == '__main__':
    unittest.main()
