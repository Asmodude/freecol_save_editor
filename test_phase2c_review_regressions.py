"""Regression checks for Phase 2C independent review findings."""
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from equipment_rules import validate_equipment
from edit_session import EditSession
from edit_preflight import unstage_checked
from edit_backend import change_equipment


class Phase2CReviewRegressions(unittest.TestCase):
    def setUp(self):
        self.root = ET.fromstring('''<save>
            <role id="model.role.default" maximum-count="1"/>
            <role id="model.role.pioneer" maximum-count="5"/>
            <unit-type id="model.unit.freeColonist">
                <ability id="model.ability.canBeEquipped" value="true"/>
            </unit-type>
            <unit id="unit:21" unitType="model.unit.freeColonist"
                  role="model.role.default" roleCount="0" movesLeft="3"/>
        </save>''')
        self.unit = next(self.root.iter('unit'))

    def test_default_role_rejects_nonzero_count(self):
        with patch('equipment_rules.movement_cap', return_value=3):
            self.assertTrue(validate_equipment(self.root, self.unit, 'model.role.default', 0))
            with self.assertRaisesRegex(ValueError, 'zero equipment count'):
                validate_equipment(self.root, self.unit, 'model.role.default', 1)

    def test_tk_stage_default_role_does_not_create_spurious_edit(self):
        with patch('equipment_rules.movement_cap', return_value=3):
            session = EditSession()
            session.stage_equipment(self.root, self.unit, 'model.role.default', 1)
            self.assertNotIn(('unit:21', 'equipment'), session.edits)
            session.stage_equipment(self.root, self.unit, 'model.role.pioneer', 4)
            self.assertIn(('unit:21', 'equipment'), session.edits)
            session.stage_equipment(self.root, self.unit, 'model.role.default', 1)
            self.assertNotIn(('unit:21', 'equipment'), session.edits)

    def test_backend_writes_zero_count_when_returning_to_default(self):
        # Full attribute rewrite through the real backend with a saved ruleset.
        raw = b'''<save><specification>
          <role id="model.role.default" maximum-count="1"/>
          <role id="model.role.pioneer" maximum-count="5"/>
          <unit-type id="model.unit.freeColonist" movement="3">
            <ability id="model.ability.canBeEquipped" value="true"/>
          </unit-type>
        </specification><game><player id="player:1"/>
          <unit id="unit:21" owner="player:1"
            unitType="model.unit.freeColonist"
            role="model.role.pioneer" roleCount="4"
            movesLeft="3"/>
        </game></save>'''
        result = change_equipment(
            raw, 'unit:21',
            ('model.role.pioneer', 4),
            ('model.role.default', 1),  # Legacy caller; backend must normalize.
        )
        unit = next(u for u in ET.fromstring(result).iter('unit')
                    if u.get('id') == 'unit:21')
        self.assertEqual(unit.get('role'), 'model.role.default')
        self.assertEqual(unit.get('roleCount'), '0')
        self.assertEqual(unit.get('movesLeft'), '3')

    def test_undo_equipment_drops_equal_source_moves_override(self):
        session = EditSession()
        equipment = ('unit:21', 'equipment')
        moves = ('unit:21', 'movesLeft')
        session.edits[equipment] = (('model.role.soldier', 1), ('model.role.dragoon', 1))
        session.edits[moves] = (3, 3)
        with patch('edit_preflight.preflight', return_value=b'<save/>') as preflight:
            unstage_checked(session, b'<save/>', equipment)
            preflight.assert_called_once_with(b'<save/>', {})
        self.assertEqual(session.edits, {})
        self.assertFalse(session.has_unexported_changes)

    def test_undo_equipment_preserves_real_movement_override(self):
        session = EditSession()
        equipment = ('unit:21', 'equipment')
        moves = ('unit:21', 'movesLeft')
        session.edits[equipment] = (('model.role.soldier', 1), ('model.role.dragoon', 1))
        session.edits[moves] = (3, 2)
        with patch('edit_preflight.preflight', return_value=b'<save/>'):
            unstage_checked(session, b'<save/>', equipment)
        self.assertEqual(session.edits, {moves: (3, 2)})


if __name__ == '__main__':
    unittest.main()
