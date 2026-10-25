"""Phase 1 game metadata always reflects original XML attributes."""
import unittest
from types import SimpleNamespace
from xml.etree.ElementTree import Element
from qt_game_properties import game_property_rows, game_property_source


class GamePropertiesTests(unittest.TestCase):
    def test_nested_options_expose_real_values_and_source(self):
        root=Element('savegame')
        game=Element('game')
        options=Element('gameOptions')
        group=Element('optionGroup',{'id':'model.option.gameOptions'})
        enabled=Element('booleanOption',{'id':'model.option.fogOfWar','value':'true'})
        group.append(enabled)
        options.append(group)
        game.append(options)
        game.append(Element('map'))
        doc=SimpleNamespace(root=root,game=game)
        rows=game_property_rows(doc)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0].get('name'),'model.option.fogOfWar')
        self.assertEqual(rows[0].get('value'),'true')
        self.assertIs(game_property_source(doc,rows[0]),enabled)
        rows[0].set('value','false')
        self.assertEqual(enabled.get('value'),'true')

    def test_provenance_and_values_are_exact_and_read_only(self):
        root=Element('savegame',{'version':'1','randomSeed':'-42'})
        game=Element('game',{'turn':'91','foo':'bar'})
        doc=SimpleNamespace(root=root,game=game)
        rows=game_property_rows(doc)
        self.assertEqual([(r.get('source'),r.get('name'),r.get('value')) for r in rows],
                         [('Savegame','randomSeed','-42'),('Savegame','version','1'),
                          ('Game','foo','bar'),('Game','turn','91')])
        rows[0].set('value','100')
        self.assertEqual(root.get('randomSeed'),'-42')


if __name__=='__main__':
    unittest.main()
