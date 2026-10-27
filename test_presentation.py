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

    def test_staged_role_updates_displayed_moves_proportionally(self):
        from xml.etree.ElementTree import fromstring
        xml = (b'<save><unit-type id="model.unit.freeColonist" movement="3"/>'
               b'<role id="model.role.soldier"/><role id="model.role.dragoon">'
               b'<modifier id="model.modifier.movementBonus" value="9" type="additive"/>'
               b'</role><player id="player:1"/>'
               b'<unit id="unit:1" unitType="model.unit.freeColonist" '
               b'owner="player:1" role="model.role.soldier" roleCount="1" movesLeft="3"/>'
               b'</save>')
        root = fromstring(xml)
        unit = next(root.iter('unit'))
        document = SimpleNamespace(root=root, players={'player:1':next(root.iter('player'))},
                                   locations={},tiles={},colony_tile_names={},unit_locations={})
        session = EditSession()
        session.stage(('unit:1','equipment'), ('model.role.soldier',1),
                      ('model.role.dragoon',1))
        self.assertEqual(presentation.row_values('Units',unit,document,session)[7], 12)
        session.stage(('unit:1','movesLeft'),3,9)
        self.assertEqual(presentation.row_values('Units',unit,document,session)[7], 9)

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
