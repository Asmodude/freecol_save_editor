"""Read-only contextual inspector contract tests."""
import unittest
from qt_detail_inspector import detail_inspection


class DetailInspectorTests(unittest.TestCase):
    def test_goods_selection(self):
        title, body = detail_inspection('Goods', ('Goods', 'Amount'), ('Cotton', '80'))
        self.assertEqual(title, 'Cotton')
        self.assertIn('Amount: 80', body)

    def test_worker_selection_preserves_all_visible_fields(self):
        title, body = detail_inspection(
            'Workers', ('ID','Unit type','Workplace','Experience'),
            ('unit:7','Free Colonist','Fort','42'))
        self.assertEqual(title, 'Free Colonist')
        self.assertIn('ID: unit:7',body)
        self.assertIn('Workplace: Fort',body)
        self.assertIn('Experience: 42',body)

    def test_missing_values_not_invented(self):
        _,body=detail_inspection('Buildings',('Building','Workers','Unspecified'),('Fort','2',''))
        self.assertNotIn('Unspecified:',body)
        self.assertIn('Workers: 2',body)


if __name__=='__main__':
    unittest.main()
