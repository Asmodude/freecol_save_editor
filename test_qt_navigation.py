"""Headless checks of Phase 1 nation navigation."""
import unittest
from types import SimpleNamespace
from xml.etree.ElementTree import Element
from qt_navigation import human_player_id, rows_for_scope


class NationNavigationTests(unittest.TestCase):
    def setUp(self):
        human=Element('player',{'id':'player:19','ai':'false','playerType':'colonial'})
        rival=Element('player',{'id':'player:20','ai':'true','playerType':'colonial'})
        native=Element('player',{'id':'player:21','ai':'true','playerType':'indian'})
        colony=Element('colony',{'owner':'player:19'})
        foreign_colony=Element('colony',{'owner':'player:20'})
        unit=Element('unit',{'owner':'player:19'})
        settlement=Element('indianSettlement',{'owner':'player:21'})
        self.doc=SimpleNamespace(players={p.get('id'):p for p in (human,rival,native)},
              records={'Players':[human,rival,native],'Colonies':[colony,foreign_colony],
                       'Units':[unit], 'Native settlements':[settlement]})

    def test_mine_does_not_mean_all_players(self):
        self.assertEqual(human_player_id(self.doc),'player:19')
        self.assertEqual(len(rows_for_scope(self.doc,'Players','mine')),1)
        self.assertEqual(len(rows_for_scope(self.doc,'Colonies','mine')),1)

    def test_rivals_and_native_settlements_are_distinct(self):
        self.assertEqual([p.get('id') for p in rows_for_scope(self.doc,'Players','rivals')],['player:20'])
        self.assertEqual(len(rows_for_scope(self.doc,'Native settlements','native')),1)

    def test_individual_rival_and_native_owner_filters(self):
        self.assertEqual([p.get('id') for p in rows_for_scope(self.doc,'Players','player:player:20')],['player:20'])
        self.assertEqual(len(rows_for_scope(self.doc,'Native settlements','native-owner:player:21')),1)
        self.assertEqual(rows_for_scope(self.doc,'Native settlements','native-owner:player:20'),[])

    def test_ambiguous_human_identity_is_not_guessed(self):
        self.doc.players['player:20'].set('ai','false')
        self.assertIsNone(human_player_id(self.doc))
        self.assertEqual(rows_for_scope(self.doc,'Players','mine'),[])


if __name__=='__main__':
    unittest.main()
