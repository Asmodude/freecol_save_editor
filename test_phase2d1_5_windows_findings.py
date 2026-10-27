"""Regression coverage for FreeCol non-personnel equipment eligibility and compact alarm layout."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
import xml.etree.ElementTree as ET
from PySide6.QtWidgets import QApplication
from types import SimpleNamespace
from edit_session import EditSession
from equipment_rules import validate_equipment
from movement_rules import EquipmentRulesIndex
from qt_equipment_editor import EquipmentEditor
from qt_numeric_stage_editor import NumericStageEditor


def fixture(identifier):
    root = ET.fromstring(f"""<save>
      <unit-type id="model.unit.{identifier}" movement="3">
        <ability id="model.ability.canBeEquipped" value="true"/>
      </unit-type>
      <role id="model.role.default" maximum-count="1"/>
      <role id="model.role.pioneer" maximum-count="5"/>
      <role id="model.role.soldier" maximum-count="1"/>
      <role id="model.role.dragoon" maximum-count="1"/>
      <role id="model.role.scout" maximum-count="1"/>
      <player id="player:1"/>
    </save>""")
    unit = ET.Element('unit', {'id': 'unit:1', 'unitType': f'model.unit.{identifier}',
                               'owner':'player:1', 'role':'model.role.default',
                               'roleCount':'0'})
    return root, unit


class NonPersonnelEligibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_non_personnel_types_refuse_every_non_default_role_even_with_positive_ability(self):
        for identifier in ('treasureTrain', 'wagonTrain', 'artillery',
                           'damagedArtillery', 'caravel', 'merchantman',
                           'galleon', 'frigate', 'privateer', 'manOWar'):
            root, unit = fixture(identifier)
            rules = EquipmentRulesIndex(root)
            for indexed in (None, rules):
                for role in ('model.role.pioneer', 'model.role.soldier',
                             'model.role.dragoon', 'model.role.scout'):
                    with self.subTest(unit=identifier, role=role, cached=indexed is not None):
                        with self.assertRaisesRegex(ValueError, 'cannot be equipped'):
                            validate_equipment(root, unit, role, 1, rules=indexed)

    def test_valid_colonist_remains_equippable(self):
        root, unit = fixture('freeColonist')
        rules = EquipmentRulesIndex(root)
        self.assertTrue(validate_equipment(root, unit, 'model.role.pioneer', 5, rules=rules))
        self.assertTrue(validate_equipment(root, unit, 'model.role.soldier', 1, rules=rules))

    def test_equipment_gui_has_only_default_for_non_personnel(self):
        root, unit = fixture('wagonTrain')
        widget = EquipmentEditor(SimpleNamespace(root=root,
                                 equipment_rules_index=EquipmentRulesIndex(root)),
                                 unit, EditSession())
        try:
            self.assertEqual(widget.selector.count(), 1)
            self.assertEqual(widget.selector.itemData(0), 'model.role.default')
            self.assertFalse(widget.selector.isEnabled())
            self.assertFalse(widget.button.isEnabled())
        finally:
            widget.deleteLater()

    def test_alarm_uses_compact_source_tooltip_without_crowding_cell(self):
        widget = NumericStageEditor(1101, 1100, staged=True,
                                    object_name='nativeSettlementAlarm',
                                    compact_source=True)
        try:
            self.assertIsNone(widget.original_label)
            self.assertIn('source value: 1100', widget.edit.toolTip())
            self.assertEqual(widget.edit.text(), '1101')
            observed = []
            widget.stage_requested.connect(observed.append)
            widget.button.click()
            self.assertEqual(observed, ['1101'])
        finally:
            widget.deleteLater()


if __name__ == '__main__':
    unittest.main()
