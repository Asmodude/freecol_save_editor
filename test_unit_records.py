"""Authoritative-unit indexing regression tests.

Cached native-settlement missionary snapshots must not enter editable lists.
"""
import unittest
import xml.etree.ElementTree as ET
from unit_records import authoritative_units


class AuthoritativeUnitTests(unittest.TestCase):
    def test_cached_missionary_is_not_a_second_unit(self):
        root = ET.fromstring("""<game><map>
          <tile id="tile:11007">
            <indianSettlement id="indianSettlement:27681" name="Xaymaca">
              <missionary><unit id="unit:34086" owner="player:19"/></missionary>
            </indianSettlement>
            <cachedTile><tile id="tile:11007">
              <indianSettlement id="indianSettlement:27681" name="Xaymaca">
                <missionary><unit id="unit:34086" owner="player:19"/></missionary>
              </indianSettlement>
            </tile></cachedTile>
          </tile>
          <tile id="tile:9"><unit id="unit:9"/></tile>
        </map></game>""")
        units = authoritative_units(root)
        self.assertEqual([unit.get("id") for unit in units], ["unit:34086", "unit:9"])

    def test_repeated_authoritative_unit_id_is_rejected(self):
        root = ET.fromstring('<game><unit id="unit:1"/><unit id="unit:1"/></game>')
        with self.assertRaisesRegex(ValueError, "Duplicate authoritative"):
            authoritative_units(root)

    def test_distinct_nested_carried_units_are_kept(self):
        root = ET.fromstring('<game><unit id="unit:1"><unit id="unit:2"/></unit></game>')
        self.assertEqual([u.get("id") for u in authoritative_units(root)], ["unit:1", "unit:2"])

    def test_ignores_non_unit_reference_nodes(self):
        root = ET.fromstring('<game><ownedUnits id="unit:1"/><unit id="unit:1"/></game>')
        self.assertEqual(len(authoritative_units(root)), 1)


if __name__ == "__main__":
    unittest.main()
