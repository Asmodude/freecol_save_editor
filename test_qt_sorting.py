"""Ensure Qt numeric sorting and display-row identity assumptions remain safe."""
import unittest
from qt_sorting import sort_key, NUMERIC_COLUMNS


class SortingTests(unittest.TestCase):
    def test_numeric_values_are_sorted_numerically(self):
        data=['100','9','21']
        self.assertEqual(sorted(data,key=lambda v:sort_key(v,True)),['9','21','100'])

    def test_ids_stay_textual(self):
        self.assertLess(sort_key('unit:10'),sort_key('unit:2'))
        self.assertNotIn('ID',NUMERIC_COLUMNS['Units'])

    def test_missing_values_sort_safely(self):
        self.assertLess(sort_key('2',True),sort_key('N/A',True))


if __name__ == '__main__':
    unittest.main()
