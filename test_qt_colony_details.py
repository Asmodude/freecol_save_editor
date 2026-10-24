"""Phase 1 read-only colony details contract."""
import unittest
from xml.etree.ElementTree import fromstring
from qt_colony_details import colony_sections, colony_detail_nodes


class ColonyDetailsTests(unittest.TestCase):
    def test_colony_buildings_workers_and_goods(self):
        colony=fromstring("""<colony id="colony:1">
            <building buildingType="model.building.fort"><unit id="unit:1" unitType="model.unit.freeColonist" role="model.role.soldier" experience="42"/></building>
            <goodsContainer><storedGoods><goods type="model.goods.cotton" amount="80"/></storedGoods></goodsContainer>
        </colony>""")
        sections=colony_sections(colony,None)
        self.assertEqual(sections['Buildings'][1],[('Fort','Stockade','2/3','1')])
        self.assertEqual(sections['Workers'][1],[('unit:1','Free Colonist','Fort','','42')])
        self.assertEqual(sections['Goods'][1],[('Cotton','80')])
    def test_goods_catalog_shows_absent_as_zero_and_preserves_xml_mapping(self):
        from types import SimpleNamespace
        colony=fromstring("""<colony><goodsContainer><storedGoods>
            <goods type="model.goods.cotton" amount="80"/>
        </storedGoods></goodsContainer></colony>""")
        doc=SimpleNamespace(units=[],goods_types=[
            'model.goods.cotton','model.goods.tools','model.goods.tradeGoods'])
        rows=colony_sections(colony,doc)['Goods'][1]
        self.assertEqual(rows,[('Cotton','80'),('Tools','0'),('Trade Goods','0')])
        nodes=colony_detail_nodes(colony,doc)['Goods']
        self.assertEqual(nodes[0].get('amount'),'80')
        self.assertIsNone(nodes[1])
        self.assertIsNone(nodes[2])
        self.assertEqual(len(colony.findall('.//goods')),1)

    def test_stationed_units_distinct_from_workplace_workers(self):
        from types import SimpleNamespace
        colony=fromstring('<colony id="colony:1" tile="tile:1" owner="player:1"><building buildingType="model.building.fort"><unit id="unit:1" unitType="model.unit.freeColonist"/></building></colony>')
        doc=SimpleNamespace(units=[
            fromstring('<unit id="unit:1" owner="player:1" location="colony:1"/>'),
            fromstring('<unit id="unit:2" owner="player:1" location="colony:1" unitType="model.unit.soldier"/>'),
            fromstring('<unit id="unit:3" owner="player:2" location="colony:1"/>')],
            location_name=lambda value: value)
        sections=colony_sections(colony,doc)
        self.assertEqual([row[0] for row in sections['Workers'][1]],['unit:1'])
        self.assertEqual([row[0] for row in sections['Stationed units'][1]],['unit:2'])

    def test_xml_nodes_match_display_rows(self):
        colony=fromstring('<colony id="colony:4"><building buildingType="model.building.fort"/><building buildingType="model.building.chapel"/><goodsContainer><storedGoods><goods type="model.goods.food" amount="12"/><goods type="model.goods.cotton" amount="5"/></storedGoods></goodsContainer></colony>')
        rows=colony_sections(colony,None)
        nodes=colony_detail_nodes(colony,None)
        self.assertEqual(len(rows['Buildings'][1]),len(nodes['Buildings']))
        self.assertEqual(len(rows['Goods'][1]),len(nodes['Goods']))
        self.assertEqual(nodes['Buildings'][1].get('buildingType'),'model.building.chapel')
        self.assertEqual(nodes['Goods'][1].get('type'),'model.goods.cotton')

    def test_empty_colony_still_has_schema(self):
        sections=colony_sections(fromstring('<colony/>'),None)
        self.assertEqual(sections['Buildings'][1],[])
        self.assertEqual(sections['Workers'][1],[])
        self.assertEqual(sections['Goods'][1],[])
        self.assertEqual(sections['Stationed units'][1],[])


if __name__=='__main__':
    unittest.main()
