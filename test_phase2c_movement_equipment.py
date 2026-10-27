"""Cross-field movement and equipment staging/undo invariants."""
import unittest
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from types import SimpleNamespace
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from qt_staged_changes_panel import StagedChangesPanel
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
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_staged_panel_undo_refuses_invalid_remaining_move(self):
        session = EditSession()
        stage_checked(session, XML, (UNIT, 'equipment'), SOLDIER, DRAGOON)
        stage_checked(session, XML, (UNIT, 'movesLeft'), 3, 12)
        panel = StagedChangesPanel(session, document=SimpleNamespace(
            xml_bytes=XML, players={}, colonies=[], native_settlements=[], units=[]))
        try:
            with patch('qt_staged_changes_panel.QMessageBox.warning') as alert:
                panel.undo_key((UNIT, 'equipment'))
            alert.assert_called_once()
            self.assertEqual(session.count, 2)
            panel.undo_key((UNIT, 'movesLeft'))
            panel.undo_key((UNIT, 'equipment'))
            self.assertEqual(session.count, 0)
        finally:
            panel.close()

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

    def test_proportional_dragoon_to_soldier_movement_table(self):
        from xml.etree.ElementTree import fromstring, tostring
        from edit_backend import change_equipment
        for prior, expected in [(12, 3), (9, 2), (6, 2), (3, 1), (0, 0)]:
            source = XML.replace(b'role="model.role.soldier"', b'role="model.role.dragoon"')
            source = source.replace(b'movesLeft="3"', ('movesLeft="%d"' % prior).encode())
            with self.subTest(prior=prior):
                updated = change_equipment(source, UNIT, DRAGOON, SOLDIER)
                unit = next(fromstring(updated).iter('unit'))
                self.assertEqual(int(unit.get('movesLeft')), expected)
                self.assertEqual(unit.get('role'), 'model.role.soldier')

    def test_full_movement_upgrade_and_role_reversal_with_staged_movement(self):
        from xml.etree.ElementTree import fromstring
        from qt_readonly import QtExplorer
        window = QtExplorer()
        try:
            root = fromstring(XML)
            unit = next(root.iter('unit'))
            window.document = SimpleNamespace(
                root=root, xml_bytes=XML,
                unit_by_id=lambda uid: unit if uid == UNIT else None)
            with patch.object(window, 'refresh_staged_view'):
                window.stage_unit_equipment(UNIT, 'model.role.dragoon', 1)
            self.assertEqual(next(fromstring(preflight(XML, window.session.edits)).iter('unit')).get('movesLeft'), '12')
            stage_checked(window.session, XML, (UNIT, 'movesLeft'), 3, 9)
            with patch.object(window, 'refresh_staged_view'):
                window.stage_unit_equipment(UNIT, 'model.role.soldier', 1)
            self.assertEqual(window.session.edits[(UNIT, 'movesLeft')], (3, 2))
            self.assertNotIn((UNIT, 'equipment'), window.session.edits)
            self.assertEqual(next(fromstring(preflight(XML, window.session.edits)).iter('unit')).get('movesLeft'), '2')
        finally:
            window.session.exported_snapshot = dict(window.session.edits)
            window.close()

    def test_movement_input_requires_explicit_stage_and_updates_after_stage(self):
        from xml.etree.ElementTree import fromstring
        from PySide6.QtWidgets import QLineEdit, QLabel, QPushButton
        from qt_overview_panel import OverviewPanel
        from presentation import effective_unit_moves
        root = fromstring(XML)
        unit = next(root.iter('unit'))
        document = SimpleNamespace(root=root)
        session = EditSession()
        stage_checked(session, XML, (UNIT, 'equipment'), SOLDIER, DRAGOON)
        panel = OverviewPanel()
        try:
            panel.setPlainText('unit:1\nMoves left: 3')
            panel.set_record('Units', unit, document, session)
            field = panel.findChild(QLineEdit, 'inlineMovesleftInput')
            status = panel.findChild(QLabel, 'inlineMovesLeftStageStatus')
            stage = panel.findChild(QPushButton, 'stageInlineMovesleft')
            self.assertIsNotNone(field)
            self.assertIsNotNone(status)
            self.assertIsNotNone(stage)
            self.assertEqual(field.text(), '12')
            field.setText('3')
            self.assertEqual(status.text(), 'Not staged')
            self.assertNotIn((UNIT, 'movesLeft'), session.edits)
            self.assertIn(b'movesLeft="12"', preflight(XML, session.edits))
            requests = []
            panel.edit_requested.connect(lambda *args: requests.append(args))
            stage.click()
            self.assertEqual(requests, [(UNIT, 'movesLeft', '3')])
            stage_checked(session, XML, (UNIT, 'movesLeft'), 3, 3)
            self.assertEqual(session.edits[(UNIT, 'movesLeft')], (3, 3))
            self.assertEqual(effective_unit_moves(unit, document, session), 3)
            result = preflight(XML, session.edits)
            self.assertIn(b'movesLeft="3"', result)
            self.assertIn(b'role="model.role.dragoon"', result)
            # An explicit 12-point edit remains staged for existing
            # dependent-undo safety, even though equipment projects 12.
            stage_checked(session, XML, (UNIT, 'movesLeft'), 3, 12)
            self.assertEqual(session.edits[(UNIT, 'movesLeft')], (3, 12))
            self.assertIn(b'movesLeft="12"', preflight(XML, session.edits))
        finally:
            panel.close()

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
        self.assertIn(b'movesLeft="12"', preflight(XML, session.edits))

if __name__ == '__main__':
    unittest.main()
