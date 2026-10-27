"""OC-001 national liberty edit uses source player value and complete export preflight."""
import unittest
import xml.etree.ElementTree as ET

from edit_session import EditSession
from edit_preflight import stage_checked, unstage_checked
from qt_overview import record_overview


_XML = (b'<savedGame><game>'
        b'<player id="player:1" playerType="colonial" gold="500" tax="10" '
        b'liberty="1234" immigration="65" immigrationRequired="100"/>'
        b'</game></savedGame>')


class NationalLibertyTests(unittest.TestCase):
    def test_player_summary_uses_authoritative_progress_attributes(self):
        from types import SimpleNamespace
        player = ET.fromstring('<player id="player:1" playerType="colonial" '
                               'gold="100" liberty="1234" immigration="65" '
                               'immigrationRequired="100"/>')
        doc = SimpleNamespace(colony_counts={}, native_counts={})
        text = record_overview('Players', player, doc)
        self.assertIn('National liberty points: 1234', text)
        self.assertIn('Immigration points: 65', text)
        self.assertIn('Immigration required: 100', text)
        self.assertNotIn('Hammers:', text)

    def test_national_liberty_edit_is_staged_and_source_immutable(self):
        session = EditSession()
        player = next(ET.fromstring(_XML).iter('player'))
        self.assertIn('liberty', EditSession.editable_fields('Players', player))
        key = ('player:1', 'liberty')
        new = session.validate(key, '1300', original=1234)
        stage_checked(session, _XML, key, 1234, new)
        self.assertEqual(session.edits[key], (1234, 1300))
        from edit_preflight import preflight
        output = preflight(_XML, session.edits)
        self.assertEqual(next(ET.fromstring(output).iter('player')).get('liberty'), '1300')
        self.assertEqual(next(ET.fromstring(_XML).iter('player')).get('liberty'), '1234')
        self.assertEqual(next(ET.fromstring(output).iter('player')).get('immigration'), '65')
        unstage_checked(session, _XML, key)
        self.assertNotIn(key, session.edits)

    def test_immutable_source_value_is_a_preflight_guard(self):
        session = EditSession()
        with self.assertRaises(ValueError):
            stage_checked(session, _XML, ('player:1', 'liberty'), 999, 1300)


if __name__ == '__main__':
    unittest.main()
