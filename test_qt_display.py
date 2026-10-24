"""Human-friendly display labels, without changing FreeCol identifiers."""
import unittest
from qt_display import display_row, display_identifier


class DisplayTests(unittest.TestCase):
    def test_native_settlement_labels(self):
        row=('indianSettlement:29829','Kayryouacou','Tamanaco','Tile (67,78)',
             'masterSugarPlanter','tools, tradeGoods, cigars')
        self.assertEqual(display_row('Native settlements',row),
             ('indianSettlement:29829','Kayryouacou','Tamanaco','Tile (67,78)',
              'Master Sugar Planter','Tools, Trade Goods, Cigars'))

    def test_unit_type_and_role_are_readable(self):
        raw=('unit:1','masterCarpenter','Owner','Tile (1,2)','pioneer','','0','3','3','5','active')
        result=display_row('Units',raw)
        self.assertEqual(result[1],'Master Carpenter')
        self.assertEqual(result[4],'Pioneer')
        self.assertEqual(raw[1],'masterCarpenter')

    def test_source_row_not_modified_and_ids_retained(self):
        row=['indianSettlement:1','Village','Tamanaco','Tile (2,3)',
             'expertFisherman','cigars, cloth']
        display_row('Native settlements',row)
        self.assertEqual(row[4],'expertFisherman')
        self.assertEqual(display_identifier('model.goods.tradeGoods'),'Trade Goods')


if __name__=='__main__':
    unittest.main()
