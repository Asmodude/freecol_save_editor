"""Headless fail-closed regression tests for equipment rules and unit deletion.

Synthetic XML only: the tests must never modify a user savegame.
"""
import unittest
import xml.etree.ElementTree as ET

from deletion_engine import UnsafeDeletion, remove_unit
from equipment_rules import validate_equipment


class EquipmentSafetyTests(unittest.TestCase):
    def setUp(self):
        self.root = ET.fromstring("""<save>
          <specification>
            <unit-type id="model.unit.freeColonist" movement="3">
              <ability id="model.ability.canBeEquipped" value="true"/>
            </unit-type>
            <unit-type id="model.unit.merchantman" movement="12">
              <ability id="model.ability.navalUnit" value="true"/>
            </unit-type>
            <role id="model.role.default" maximum-count="1"/>
            <role id="model.role.soldier" maximum-count="2"/>
            <role id="model.role.pioneer" maximum-count="1"/>
          </specification>
          <game>
            <player id="player:1"/>
            <unit id="unit:1" unitType="model.unit.freeColonist"
                  owner="player:1" role="model.role.default" movesLeft="3"/>
            <unit id="unit:2" unitType="model.unit.merchantman"
                  owner="player:1" role="model.role.default" movesLeft="12"/>
          </game>
        </save>""")
        self.colonist = next(e for e in self.root.iter("unit") if e.get("id") == "unit:1")
        self.ship = next(e for e in self.root.iter("unit") if e.get("id") == "unit:2")

    def test_equippable_colonist_can_be_soldier(self):
        self.assertTrue(validate_equipment(self.root, self.colonist, "model.role.soldier", 1))

    def test_equipment_count_must_match_ruleset(self):
        with self.assertRaisesRegex(ValueError, "count"):
            validate_equipment(self.root, self.colonist, "model.role.soldier", 3)
        with self.assertRaisesRegex(ValueError, "count"):
            validate_equipment(self.root, self.colonist, "model.role.soldier", 0)

    def test_unknown_role_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported equipment role"):
            validate_equipment(self.root, self.colonist, "model.role.doesNotExist", 1)

    def test_naval_unit_cannot_equip_soldier(self):
        with self.assertRaisesRegex(ValueError, "naval"):
            validate_equipment(self.root, self.ship, "model.role.soldier", 1)

    def test_equipping_requires_explicit_ability(self):
        ability = self.root.find(".//unit-type[@id='model.unit.freeColonist']/ability")
        ability.set("value", "false")
        with self.assertRaisesRegex(ValueError, "explicitly support equipping"):
            validate_equipment(self.root, self.colonist, "model.role.pioneer", 1)

    def test_unknown_ruleset_unit_type_fails_closed(self):
        self.colonist.set("unitType", "model.unit.unknown")
        with self.assertRaises(ValueError):
            validate_equipment(self.root, self.colonist, "model.role.soldier", 1)


class UnitDeletionSafetyTests(unittest.TestCase):
    @staticmethod
    def document(*, extra="", cargo="", unit_id="unit:1"):
        return (f'<save><game><map><tile id="tile:1">'
                f'<unit id="{unit_id}" owner="player:1" location="tile:1">'
                f'{cargo}</unit></tile></map>{extra}</game></save>').encode()

    def test_safe_unit_removes_only_target(self):
        xml = self.document(extra='<unit id="unit:2" owner="player:1"></unit>')
        result = remove_unit(xml, "unit:1")
        tree = ET.fromstring(result)
        self.assertEqual([u.get("id") for u in tree.iter("unit")], ["unit:2"])
        self.assertEqual(tree.find(".//tile").get("id"), "tile:1")

    def test_delete_does_not_mutate_input_bytes(self):
        original = self.document()
        snapshot = original[:]
        remove_unit(original, "unit:1")
        self.assertEqual(original, snapshot)

    def test_unknown_external_reference_rejected(self):
        xml = self.document(extra='<mystery target="unit:1"/>')
        with self.assertRaises(UnsafeDeletion):
            remove_unit(xml, "unit:1")

    def test_carrier_with_goods_rejected(self):
        xml = self.document(cargo='<goods id="goods:1"></goods>')
        with self.assertRaisesRegex(UnsafeDeletion, "Carrier"):
            remove_unit(xml, "unit:1")

    def test_ambiguous_unit_id_rejected(self):
        xml = self.document(extra='<unit id="unit:1"></unit>')
        with self.assertRaises(UnsafeDeletion):
            remove_unit(xml, "unit:1")

    def test_invalid_identifier_rejected(self):
        with self.assertRaises(UnsafeDeletion):
            remove_unit(self.document(), "unit:1\"><malicious")

    def test_unexpected_unit_container_rejected(self):
        xml = b'<save><game><unit id="unit:1" owner="player:1" location="tile:1"></unit></game></save>'
        with self.assertRaisesRegex(UnsafeDeletion, "container"):
            remove_unit(xml, "unit:1")


if __name__ == "__main__":
    unittest.main()
