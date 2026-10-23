"""Headless checks for extracted presentation shapes and legacy editability."""
import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace
import presentation
from edit_session import EditSession


class PresentationTests(unittest.TestCase):
    def test_text_helpers(self):
        self.assertEqual(presentation.short('model.unit.freeColonist'),'freeColonist')
        self.assertEqual(presentation.readable('model.building.carpenterHouse'),'Carpenter House')
        self.assertEqual(presentation.experience_towards({}),'—')
        self.assertEqual(presentation.building_tier('fort'),('Stockade','2/3'))

    def test_player_tuple_and_staged_gold(self):
        player=ET.Element('player',{'id':'player:1','username':'Tester','nationId':'model.nation.danish',
                                  'playerType':'colonial','gold':'10','tax':'3','ai':'false'})
        doc=SimpleNamespace(players={'player:1':player},colony_counts={'player:1':2},
                            native_counts={},root=None)
        session=EditSession()
        session.stage(('player:1','gold'),10,15)
        row=presentation.row_values('Players',player,doc,session)
        self.assertEqual(len(row),11)
        self.assertEqual(row[6],15)
        self.assertEqual(row[4],2)

    def test_edit_permissions_match_legacy_overview(self):
        edit=EditSession()
        normal=ET.Element('player',{'gold':'50'})
        native=ET.Element('player',{'gold':'-2147483648'})
        self.assertEqual(edit.editable_fields('Players',normal),{'gold','tax'})
        self.assertEqual(edit.editable_fields('Players',native),{'tax'})
        self.assertEqual(edit.editable_fields('Units',normal),{'experience','movesLeft'})
        self.assertEqual(edit.editable_fields('Colonies',normal),{'sonsOfLiberty'})
        self.assertEqual(edit.editable_fields('Native settlements',normal),{'learnableSkill'})


if __name__=='__main__':
    unittest.main()
