"""Founding Fathers presentation contract: no XML IDs or recruiting status in Congress."""
import unittest
from pathlib import Path


class FatherViewContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=Path(__file__).with_name('qt_readonly.py').read_text(encoding='utf-8')

    def test_recruited_only_and_separate_banner(self):
        self.assertIn("element.get('status') != 'Recruited'",self.source)
        self.assertIn("self.father_banner.setVisible",self.source)
        self.assertIn("self.inspect_recruiting_father",self.source)

    def test_names_not_raw_ids_in_upper_table(self):
        self.assertIn("'Founding Fathers': ('Founding Father', 'Status')",self.source)
        self.assertIn("element.get('name'), element.get('status')",self.source)
        self.assertIn("self.father_portraits.get(rows[row][0].get('id'))",self.source)


if __name__=='__main__':
    unittest.main()
