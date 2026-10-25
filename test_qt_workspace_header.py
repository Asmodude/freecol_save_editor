"""Workspace header metadata must follow actual saved scope, never mockup data."""
import unittest
from types import SimpleNamespace
from xml.etree.ElementTree import Element
from qt_workspace_header import workspace_identity

class WorkspaceHeaderTests(unittest.TestCase):
    def setUp(self):
        human = Element('player', {'id':'p1','ai':'false','playerType':'colonial',
                                   'nationId':'model.nation.danish'})
        rival = Element('player', {'id':'p2','ai':'true','playerType':'colonial',
                                   'nationId':'model.nation.french'})
        colony = Element('colony', {'id':'c1','owner':'p2','name':'Fort Louis'})
        self.doc = SimpleNamespace(players={'p1':human,'p2':rival},
                                   colonies=[colony], native_settlements=[],
                                   units=[], records={'Colonies':[colony],
                                                      'Players':[human,rival],
                                                      'Units':[],
                                                      'Native settlements':[]})

    def test_no_document(self):
        title, subtitle, key, native, hint = workspace_identity(None,'Players','mine')
        self.assertEqual(title,'Savegame Explorer')
        self.assertIsNone(key)

    def test_rival_colonies(self):
        title, subtitle, key, native, hint = workspace_identity(
            self.doc, 'Colonies', 'player:p2')
        self.assertEqual(title,'French — Colonies (1)')
        self.assertEqual(key,'model.nation.french')
        self.assertFalse(native)
        self.assertEqual(hint,'Filter colonies…')

    def test_direct_colony_title_and_owner(self):
        title, subtitle, key, native, hint = workspace_identity(
            self.doc, 'Colonies', 'colony-id:c1')
        self.assertEqual(title,'French — Fort Louis')
        self.assertEqual(key,'model.nation.french')

    def test_game_properties_without_assumed_owner(self):
        title, subtitle, key, native, hint = workspace_identity(
            self.doc, 'Game properties', 'game')
        self.assertEqual(title,'Game properties')
        self.assertIsNone(key)

if __name__ == '__main__':
    unittest.main()
