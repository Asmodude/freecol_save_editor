"""Phase 1 read-only colony details contract."""
import unittest
from xml.etree.ElementTree import fromstring
from qt_colony_details import colony_sections


class ColonyDetailsTests(unittest.TestCase):
    def test_colony_buildings_workers_and_goods(self):
        colony=fromstring("""<colony id="colony:1">
            <building buildingType="model.building.fort"><unit id="unit:1" unitType="model.unit.freeColonist" role="model.role.soldier" experience="42"/></building>
            <goodsContainer><storedGoods><goods type="model.goods.cotton" amount="80"/></storedGoods></goodsContainer>
        </colony>""")
        sections=colony_sections(colony,None)
        self.assertEqual(sections['Buildings'][1],[('Fort','Stockade','2/3','1')])
        self.assertEqual(sections['Units'][1],[('unit:1','Free Colonist','Soldier','42')])
        self.assertEqual(sections['Goods'][1],[('Cotton','80')])
    def test_empty_colony_still_has_schema(self):
        sections=colony_sections(fromstring('<colony/>'),None)
        self.assertEqual(sections['Buildings'][1],[])
        self.assertEqual(sections['Units'][1],[])
        self.assertEqual(sections['Goods'][1],[])


if __name__=='__main__':
    unittest.main()
