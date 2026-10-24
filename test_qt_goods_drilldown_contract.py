"""Source-level regression checks for the Phase 1 nation-to-colony drill-down."""
from pathlib import Path
import unittest


class DrilldownContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=Path(__file__).with_name('qt_readonly.py').read_text(encoding='utf-8')

    def test_drilldown_is_explicit_and_read_only(self):
        self.assertIn("self.jump_colony_button.clicked.connect(self.open_breakdown_colony)",self.source)
        self.assertIn("if section == 'By colony':",self.source)
        self.assertIn("self.navigation.setCurrentItem(destination)",self.source)
        self.assertIn("self.tabs.setCurrentWidget(table)",self.source)
        self.assertIn("if len(matches) != 1",self.source)
        self.assertIn("self.jump_colony_button.setEnabled(False)",self.source)
        self.assertIn("breakdown.selectRow(0)",self.source)
        self.assertIn("self.inspect_detail('By colony')",self.source)
        self.assertIn("table.selectedItems()",self.source)


if __name__ == '__main__':
    unittest.main()
