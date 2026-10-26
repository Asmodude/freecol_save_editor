"""Cross-field movement and equipment staging/undo invariants."""
import unittest
from edit_session import EditSession
from edit_preflight import stage_checked, unstage_checked, preflight

UNIT = "unit:1"
DEFAULT = ("model.role.default", 1)
DRAGOON = ("model.role.dragoon", 1)
SOLDIER = ("model.role.soldier", 1)
XML = (b'<save><specification>'
       b'<unit-types><unit-type id="model.unit.freeColonist" movement="3">'
       b'<ability id="model.ability.canBeEquipped" value="true"></ability></unit-type></unit-types>'
       b'<roles><role id="model.role.default" maximum-count="1"></role>'
       b'<role id="model.role.soldier" maximum-count="1"></role>'
       b'<role id="model.role.dragoon" maximum-count="1">'
       b'<modifier id="model.modifier.movementBonus" type="additive" value="9"></modifier>'
       b'</role></roles></specification><game><player id="player:1"></player>'
       b'<unit id="unit:1" unitType="model.unit.freeColonist" owner="player:1" '
       b'role="model.role.soldier" roleCount="1" movesLeft="3"></unit></game></save>')

class EquipmentMovementPreflightTests(unittest.TestCase):
    def test_increased_cap_allows_moves_and_refuses_undo_equipment(self):
        session = EditSession()
        stage_checked(session, XML, (UNIT, 'equipment'), SOLDIER, DRAGOON)
        stage_checked(session, XML, (UNIT, 'movesLeft'), 3, 12)
        result = preflight(XML, session.edits)
        self.assertIn(b'movesLeft="12"', result)
        before = dict(session.edits)
        with self.assertRaisesRegex(ValueError, 'Movement allowed range'):
            unstage_checked(session, XML, (UNIT, 'equipment'))
        self.assertEqual(session.edits, before)
        unstage_checked(session, XML, (UNIT, 'movesLeft'))
        unstage_checked(session, XML, (UNIT, 'equipment'))
        self.assertEqual(session.count, 0)

    def test_lowering_cap_rejects_out_of_range_move(self):
        session = EditSession()
        stage_checked(session, XML, (UNIT, 'equipment'), SOLDIER, DRAGOON)
        stage_checked(session, XML, (UNIT, 'movesLeft'), 3, 12)
        before = dict(session.edits)
        with self.assertRaisesRegex(ValueError, 'Movement allowed range'):
            stage_checked(session, XML, (UNIT, 'equipment'), SOLDIER, SOLDIER)
        self.assertEqual(session.edits, before)
        stage_checked(session, XML, (UNIT, 'movesLeft'), 3, 2)
        stage_checked(session, XML, (UNIT, 'equipment'), SOLDIER, SOLDIER)
        self.assertNotIn((UNIT, 'equipment'), session.edits)
        self.assertEqual(session.edits[(UNIT, 'movesLeft')], (3, 2))

    def test_movement_above_source_cap_refused_before_equipment(self):
        session = EditSession()
        with self.assertRaisesRegex(ValueError, 'Movement allowed range'):
            stage_checked(session, XML, (UNIT, 'movesLeft'), 3, 12)
        self.assertEqual(session.count, 0)

    def test_equipment_clamp_and_moves_source_consistency(self):
        session = EditSession()
        stage_checked(session, XML, (UNIT, 'equipment'), SOLDIER, DRAGOON)
        stage_checked(session, XML, (UNIT, 'movesLeft'), 3, 7)
        self.assertIn(b'movesLeft="7"', preflight(XML, session.edits))
        unstage_checked(session, XML, (UNIT, 'movesLeft'))
        self.assertEqual(session.count, 1)
        self.assertIn(b'movesLeft="3"', preflight(XML, session.edits))

if __name__ == '__main__':
    unittest.main()
