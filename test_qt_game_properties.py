"""Phase 1 game metadata always reflects original XML attributes."""
import unittest
from types import SimpleNamespace
from xml.etree.ElementTree import Element
from qt_game_properties import game_property_rows


class GamePropertiesTests(unittest.TestCase):
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
