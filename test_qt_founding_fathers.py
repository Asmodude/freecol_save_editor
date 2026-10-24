"""Read-only Founding Father extraction from FreeCol Player XML."""
import unittest
from xml.etree.ElementTree import fromstring
from types import SimpleNamespace
from qt_founding_fathers import father_rows, father_source_node
from qt_navigation import rows_for_scope


class FoundingFatherTests(unittest.TestCase):
    def test_recruited_offered_current_and_no_mutation(self):
        player=fromstring("""<player id="player:1" playerType="colonial"
          ai="false" currentFather="model.foundingFather.peterMinuit">
          <foundingFathers arraySize="2" x0="model.foundingFather.benjaminFranklin"
                          x1="model.foundingFather.jacobFugger"/>
          <offeredFathers arraySize="2" x0="model.foundingFather.peterMinuit"
                         x1="model.foundingFather.francisDrake"/>
        </player>""")
        before=__import__('xml.etree.ElementTree',fromlist=['tostring']).tostring(player)
        rows=father_rows(player)
        actual={r.get('name'):r.get('status') for r in rows}
        self.assertEqual(actual['Benjamin Franklin'],'Recruited')
        self.assertEqual(actual['Jacob Fugger'],'Recruited')
        self.assertEqual(actual['Peter Minuit'],'Recruiting')
        self.assertEqual(actual['Francis Drake'],'Offered')
        self.assertEqual(before,__import__('xml.etree.ElementTree',fromlist=['tostring']).tostring(player))

    def test_genuine_xml_source_for_recruited_and_recruiting(self):
        player=fromstring("""<player id="player:1" ai="false"
             currentFather="model.foundingFather.simonBolivar">
             <foundingFathers x0="model.foundingFather.benjaminFranklin"/>
             </player>""")
        doc=SimpleNamespace(players={'player:1':player})
        records={r.get('status'):r for r in father_rows(player)}
        self.assertIs(father_source_node(doc,records['Recruiting']),player)
        self.assertIs(father_source_node(doc,records['Recruited']),player.find('foundingFathers'))
        self.assertIsNone(father_source_node(SimpleNamespace(players={}),records['Recruiting']))

    def test_scope_is_player_specific(self):
        a=fromstring('<player id="player:1" playerType="colonial" ai="false"><foundingFathers x0="model.foundingFather.francisDrake"/></player>')
        b=fromstring('<player id="player:2" playerType="colonial" ai="true"><foundingFathers x0="model.foundingFather.peterMinuit"/></player>')
        doc=SimpleNamespace(players={'player:1':a,'player:2':b})
        self.assertEqual(rows_for_scope(doc,'Founding Fathers','mine')[0].get('name'),'Francis Drake')
        self.assertEqual(rows_for_scope(doc,'Founding Fathers','player:player:2')[0].get('name'),'Peter Minuit')
        self.assertEqual(rows_for_scope(doc,'Founding Fathers','player:missing'),[])


if __name__=='__main__':
    unittest.main()
