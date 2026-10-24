"""Nation warehouse totals: scope, zeros and source XML non-mutation."""
import unittest
from xml.etree.ElementTree import fromstring, tostring
from types import SimpleNamespace
from qt_national_goods import national_goods, colony_goods_breakdown
from qt_navigation import rows_for_scope


class NationalGoodsTests(unittest.TestCase):
    def test_breakdown_includes_zero_colonies_but_excludes_rivals(self):
        players={'player:1':fromstring('<player id="player:1"/>')}
        a=fromstring('<colony owner="player:1" name="Alpha"><goodsContainer><storedGoods><goods type="model.goods.tools" amount="12"/></storedGoods></goodsContainer></colony>')
        b=fromstring('<colony owner="player:1" name="Beta"/>')
        c=fromstring('<colony owner="player:2" name="Enemy"><goodsContainer><storedGoods><goods type="model.goods.tools" amount="800"/></storedGoods></goodsContainer></colony>')
        doc=SimpleNamespace(players=players,colonies=[a,b,c])
        self.assertEqual(colony_goods_breakdown(doc,'player:1','model.goods.tools'),
                         [('Alpha','12'),('Beta','0')])
        self.assertEqual(colony_goods_breakdown(doc,'missing','model.goods.tools'),[])

    def test_totals_only_owned_colony_stores_and_zero_catalog(self):
        a=fromstring('<colony owner="player:1"><goodsContainer><storedGoods><goods type="model.goods.tools" amount="100"/></storedGoods></goodsContainer></colony>')
        b=fromstring('<colony owner="player:1"><goodsContainer><storedGoods><goods type="model.goods.tools" amount="20"/><goods type="model.goods.food" amount="8"/></storedGoods></goodsContainer></colony>')
        c=fromstring('<colony owner="player:2"><goodsContainer><storedGoods><goods type="model.goods.tools" amount="999"/></storedGoods></goodsContainer></colony>')
        players={'player:1':fromstring('<player id="player:1" ai="false" playerType="colonial"/>'),'player:2':fromstring('<player id="player:2" ai="true" playerType="colonial"/>')}
        doc=SimpleNamespace(colonies=[a,b,c],players=players,goods_types=['model.goods.food','model.goods.tools','model.goods.tradeGoods'])
        before=[tostring(v) for v in doc.colonies]
        mine={row.get('name'):(row.get('amount'),row.get('colonies')) for row in rows_for_scope(doc,'National Goods','mine')}
        self.assertEqual(mine,{'Food':('8','1'),'Tools':('120','2'),'Trade Goods':('0','0')})
        rival={row.get('name'):row.get('amount') for row in rows_for_scope(doc,'National Goods','player:player:2')}
        self.assertEqual(rival['Tools'],'999')
        self.assertEqual(before,[tostring(v) for v in doc.colonies])
        self.assertEqual(national_goods(doc,'nonexistent'),[])


if __name__=='__main__':
    unittest.main()
