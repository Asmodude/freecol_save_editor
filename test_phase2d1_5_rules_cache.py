"""Cached and uncached FreeCol equipment validation must have identical semantics."""
import unittest
import xml.etree.ElementTree as ET
from equipment_rules import validate_equipment
from movement_rules import EquipmentRulesIndex, movement_cap


def sample_root():
    return ET.fromstring("""<save>
      <specification>
        <unit-types>
          <unit-type id="model.unit.freeColonist" movement="3">
            <ability id="model.ability.canBeEquipped" value="true"/>
          </unit-type>
          <unit-type id="model.unit.merchantman" movement="12">
            <ability id="model.ability.navalUnit" value="true"/>
          </unit-type>
        </unit-types>
        <roles>
          <role id="model.role.default" maximum-count="1"/>
          <role id="model.role.pioneer" maximum-count="5"/>
          <role id="model.role.soldier" maximum-count="1"/>
          <role id="model.role.dragoon" maximum-count="1">
            <modifier id="model.modifier.movementBonus" type="additive" value="9"/>
          </role>
          <role id="model.role.scout" maximum-count="1"/>
        </roles>
      </specification>
      <game>
        <player id="player:1" />
      </game>
    </save>""")


class CachedRulesParityTests(unittest.TestCase):
    def test_role_and_movement_semantics_match_uncached(self):
        root = sample_root()
        rules = EquipmentRulesIndex(root)
        for unit_type in ('model.unit.freeColonist', 'model.unit.merchantman',
                          'model.unit.missing'):
            unit = ET.Element('unit', {'unitType': unit_type, 'owner': 'player:1'})
            for role in ('model.role.default', 'model.role.pioneer',
                         'model.role.dragoon', 'model.role.missing'):
                for count in (0, 1, 4, 6):
                    with self.subTest(type=unit_type, role=role, count=count):
                        outcomes = []
                        for index in (None, rules):
                            try:
                                outcomes.append(('ok', validate_equipment(
                                    root, unit, role, count, rules=index)))
                            except ValueError as exc:
                                outcomes.append((type(exc).__name__, str(exc)))
                        self.assertEqual(outcomes[0], outcomes[1])

    def test_duplicate_roles_are_refused_in_both_paths(self):
        root = sample_root()
        root.find('./specification/roles').append(
            ET.Element('role', {'id':'model.role.pioneer', 'maximum-count':'5'}))
        rules = EquipmentRulesIndex(root)
        unit = ET.Element('unit', {'unitType':'model.unit.freeColonist',
                                    'owner':'player:1'})
        for index in (None, rules):
            with self.assertRaisesRegex(ValueError, 'uniquely'):
                validate_equipment(root, unit, 'model.role.pioneer', 1, rules=index)

    def test_owner_modifier_and_missing_owner_refusals_match(self):
        for modified in (False, True):
            root = sample_root()
            if modified:
                ET.SubElement(root.find('./game/player'), 'modifier',
                    {'id':'model.modifier.movementBonus', 'value':'1'})
            rules = EquipmentRulesIndex(root)
            for owner in ('player:1', 'player:missing'):
                unit = ET.Element('unit', {'unitType':'model.unit.freeColonist',
                                           'owner':owner, 'role':'model.role.default'})
                outcomes = []
                for index in (None, rules):
                    try:
                        outcomes.append(('ok', movement_cap(root, unit, rules=index)))
                    except ValueError as exc:
                        outcomes.append((type(exc).__name__, str(exc)))
                self.assertEqual(outcomes[0], outcomes[1])


if __name__ == '__main__':
    unittest.main()
