"""Global search matches names/IDs without mutating indexed savegame elements."""
import unittest
from types import SimpleNamespace
from xml.etree.ElementTree import Element
from qt_global_search import global_results


class GlobalSearchTests(unittest.TestCase):
    def setUp(self):
        self.player=Element('player',{'id':'player:1','username':'Morten Olsson','nationId':'model.nation.danish'})
        self.colony=Element('colony',{'id':'colony:2','name':'Christiansborg','owner':'player:1'})
        self.unit=Element('unit',{'id':'unit:3','unitType':'model.unit.masterCarpenter','owner':'player:1'})
        self.native=Element('indianSettlement',{'id':'indianSettlement:4','name':'Kayryouacou','owner':'player:native'})
        self.doc=SimpleNamespace(records={'Players':[self.player],'Colonies':[self.colony],
                    'Units':[self.unit],'Native settlements':[self.native]},
                    owner_name=lambda key: 'Morten Olsson' if key=='player:1' else 'Arawak')

    def test_cross_category_search(self):
        self.assertEqual(global_results(self.doc,'Christiansborg')[0][1],self.colony)
        self.assertEqual(global_results(self.doc,'Master Carpenter')[0][1],self.unit)
        self.assertEqual(global_results(self.doc,'Kayryouacou')[0][1],self.native)
        self.assertEqual(global_results(self.doc,'unit:3')[0][1],self.unit)
        self.assertEqual(global_results(self.doc,'  '),[])

    def test_results_are_identity_preserving(self):
        self.assertIs(global_results(self.doc,'Christiansborg')[0][1],self.colony)
        self.assertEqual(global_results(self.doc,'Morten',limit=1)[0][1],self.player)


if __name__=='__main__':
    unittest.main()
