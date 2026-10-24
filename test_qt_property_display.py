"""Long saved values are shortened only for presentation."""
import unittest
from qt_property_display import compact_property_value

class PropertyDisplayTests(unittest.TestCase):
    def test_long_state_does_not_expand_table(self):
        raw='ACED0005'+'7A'*1000
        shown=compact_property_value(raw)
        self.assertEqual(len(shown),96)
        self.assertTrue(shown.endswith('…'))
        self.assertEqual(raw,'ACED0005'+'7A'*1000)

    def test_normal_values_unchanged(self):
        self.assertEqual(compact_property_value('unit:32247'),'unit:32247')
        self.assertEqual(compact_property_value(''),'')
        self.assertEqual(compact_property_value(None),'')
        self.assertEqual(compact_property_value('x'*96),'x'*96)

if __name__=='__main__':
    unittest.main()
