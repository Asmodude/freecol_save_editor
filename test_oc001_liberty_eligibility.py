"""OC-001 independent review M2: only living nations that can elect Fathers."""
import unittest
from xml.etree import ElementTree as ET

from qt_liberty_eligibility import can_edit_national_liberty
from edit_backend import change_field

HEAD = ('<savedGame><european-nation-type id="model.nationType.default">'
        '<ability id="model.ability.electFoundingFather" value="true"/>'
        '</european-nation-type>'
        '<european-nation-type id="model.nationType.ref"/>'
        '<european-nation-type id="model.nationType.trade" '
        'extends="model.nationType.default"/>'
        '<game>')
TAIL = '</game></savedGame>'


def xml_player(kind='model.nationType.default', dead='false', player_type='colonial'):
    return (HEAD + '<player id="player:1" playerType="' + player_type
            + '" nationType="' + kind + '" dead="' + dead
            + '" gold="400" liberty="20"/>' + TAIL).encode()


class LibertyEligibilityTests(unittest.TestCase):
    def test_living_colonial_with_ability_eligible_and_exports(self):
        data = xml_player()
        root = ET.fromstring(data)
        player = next(root.iter('player'))
        self.assertTrue(can_edit_national_liberty(root, player))
        edited = change_field(data, 'player:1', 'liberty', 20, 30)
        self.assertEqual(next(ET.fromstring(edited).iter('player')).get('liberty'), '30')

    def test_inherited_founder_ability_accepted(self):
        data = xml_player('model.nationType.trade')
        root = ET.fromstring(data)
        self.assertTrue(can_edit_national_liberty(root, next(root.iter('player'))))

    def test_unknown_enemy_ref_and_dead_player_refused(self):
        for data in (xml_player('model.nationType.ref'),
                     xml_player('model.nationType.missing'),
                     xml_player(dead='true'), xml_player(player_type='native')):
            with self.subTest(data=data[:80]):
                root = ET.fromstring(data)
                self.assertFalse(can_edit_national_liberty(root, next(root.iter('player'))))
                with self.assertRaisesRegex(ValueError, 'eligible'):
                    change_field(data, 'player:1', 'liberty', 20, 30)

    def test_explicit_disabled_ability_overrides_inheritance(self):
        data = xml_player('model.nationType.trade')
        data = data.replace(b'<game>', b'<european-nation-type id="model.nationType.blocked" '
                            b'extends="model.nationType.default">'
                            b'<ability id="model.ability.electFoundingFather" value="false"/>'
                            b'</european-nation-type><game>')
        data = data.replace(b'nationType="model.nationType.trade"', b'nationType="model.nationType.blocked"')
        root = ET.fromstring(data)
        self.assertFalse(can_edit_national_liberty(root, next(root.iter('player'))))


if __name__ == '__main__':
    unittest.main()
