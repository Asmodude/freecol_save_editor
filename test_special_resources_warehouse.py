"""OC-001 warehouse lists must exclude virtual production/progress resources."""
import unittest
from types import SimpleNamespace
from xml.etree.ElementTree import fromstring

from qt_colony_details import goods_catalog, colony_sections, colony_detail_nodes
from qt_national_goods import national_goods, colony_goods_breakdown, transported_goods_breakdown
from qt_special_resources import VIRTUAL_GOODS, is_warehouse_good


class SpecialResourcesWarehouseTests(unittest.TestCase):
    def setUp(self):
        self.colony = fromstring(
            '<colony id="colony:1" name="Christiansborg" owner="player:1">'
            '<goodsContainer><storedGoods>'
            '<goods type="model.goods.bells" amount="101"/>'
            '<goods type="model.goods.crosses" amount="102"/>'
            '<goods type="model.goods.hammers" amount="103"/>'
            '<goods type="model.goods.tools" amount="47"/>'
            '</storedGoods></goodsContainer></colony>')
        self.player = fromstring('<player id="player:1"/>')
        self.document = SimpleNamespace(
            goods_types=[*VIRTUAL_GOODS, 'model.goods.tools', 'model.goods.lumber'],
            colonies=[self.colony], players={'player:1': self.player}, units=[],
            unit_by_id=lambda uid: None)

    def test_colony_catalog_and_detail_rows_exclude_virtual_goods(self):
        catalog = goods_catalog(self.colony, self.document)
        self.assertEqual({kind for kind, _ in catalog},
                         {'model.goods.tools', 'model.goods.lumber'})
        rows = colony_sections(self.colony, self.document)['Goods'][1]
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(colony_detail_nodes(self.colony, self.document)['Goods']), 2)
        # Filtering is presentation-only.
        self.assertEqual(len(self.colony.findall('./goodsContainer/storedGoods/goods')), 4)

    def test_national_inventory_and_breakdowns_exclude_virtual_goods(self):
        rows = national_goods(self.document, 'player:1')
        self.assertEqual({row.get('id') for row in rows},
                         {'model.goods.tools', 'model.goods.lumber'})
        tools = next(row for row in rows if row.get('id') == 'model.goods.tools')
        self.assertEqual(tools.get('amount'), '47')
        for kind in VIRTUAL_GOODS:
            self.assertEqual(colony_goods_breakdown(self.document, 'player:1', kind), [])
            self.assertEqual(transported_goods_breakdown(self.document, 'player:1', kind), [])

    def test_goods_identity_is_explicit_and_physical_goods_unchanged(self):
        self.assertFalse(is_warehouse_good(None))
        for kind in VIRTUAL_GOODS:
            self.assertFalse(is_warehouse_good(kind))
        self.assertTrue(is_warehouse_good('model.goods.tools'))


if __name__ == '__main__':
    unittest.main()
