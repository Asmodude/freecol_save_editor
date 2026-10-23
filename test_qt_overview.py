"""Phase 1 overview read-only summaries."""
import unittest
from types import SimpleNamespace
from xml.etree.ElementTree import fromstring
from qt_overview import record_overview


class OverviewTests(unittest.TestCase):
    def test_colony_overview_counts_real_workplaces_and_stores(self):
        colony=fromstring("""<colony id="colony:1" owner="player:1" tile="tile:1"
          name="Christiansborg" established="1495" liberty="20">
          <building buildingType="model.building.fort">
            <unit id="unit:1" unitType="model.unit.freeColonist"/>
          </building>
          <goodsContainer><storedGoods><goods type="model.goods.food" amount="25"/></storedGoods></goodsContainer>
        </colony>""")
        doc=SimpleNamespace(units=[],owner_name=lambda _: 'Denmark',
            location_name=lambda _: 'Christiansborg')
        text=record_overview('Colonies',colony,doc)
        self.assertIn('Workplace workers: 1',text)
        self.assertIn('Stationed units: 0',text)
        self.assertIn('Buildings: 1',text)
        self.assertIn('Warehouse goods total: 25',text)
        self.assertIn('Owner: Denmark',text)

    def test_empty_colony_avoids_invented_statistics(self):
        doc=SimpleNamespace(units=[],owner_name=lambda _: '',location_name=lambda _: '')
        text=record_overview('Colonies',fromstring('<colony name="Empty"/>'),doc)
        self.assertNotIn('Established:',text)
        self.assertIn('Workplace workers: 0',text)


if __name__=='__main__':
    unittest.main()
