"""Phase 2D-0 Package A: baseline characterization of deletion safety.

The expected-failure tests are known corruption reproductions, NOT acceptance.
Remove expectedFailure as soon as M1/M2 fixes enforce the intended invariants.
Synthetic saves only; no real user saves checked in.
"""
import unittest
from xml.etree import ElementTree as ET
from deletion_engine import remove_unit, remove_settlement, UnsafeDeletion


class DeletionBaselinePackageATests(unittest.TestCase):
    def test_explicit_close_target_preserves_adjacent_unit(self):
        xml = (b'<save><game><map><tile id="tile:1">'
               b'<unit id="unit:5" owner="player:1" location="tile:1"></unit>'
               b'<unit id="unit:6" owner="player:1" location="tile:1"></unit>'
               b'</tile></map></game></save>')
        result = remove_unit(xml, 'unit:5')
        self.assertEqual([u.get('id') for u in ET.fromstring(result).iter('unit')], ['unit:6'])
        self.assertEqual(result.count(b'unit:6'), 1)

    @unittest.expectedFailure  # Known unsafe next-closing-tag heuristic; fixed in M1/M2
    def test_self_closing_target_must_preserve_adjacent_unit(self):
        xml = (b'<save><game><map><tile id="tile:1">'
               b'<unit id="unit:5" owner="player:1" location="tile:1"/>'
               b'<unit id="unit:6" owner="player:1" location="tile:1"></unit>'
               b'</tile></map></game></save>')
        untouched = xml[:]
        result = remove_unit(xml, 'unit:5')
        self.assertEqual(xml, untouched, 'Input must stay byte-identical')
        self.assertEqual([u.get('id') for u in ET.fromstring(result).iter('unit')], ['unit:6'])
        self.assertIn(b'unit:6', result)

    def test_unsupported_carrier_cargo_is_refused(self):
        xml = (b'<save><game><map><tile id="tile:1">'
               b'<unit id="unit:5" owner="player:1" location="tile:1">'
               b'<goods id="goods:1"/></unit></tile></map></game></save>')
        with self.assertRaises(UnsafeDeletion):
            remove_unit(xml, 'unit:5')

    def test_unknown_reference_is_refused(self):
        xml = (b'<save><game><map><tile id="tile:1">'
               b'<unit id="unit:5" owner="player:1" location="tile:1"/>'
               b'</tile></map><thing destination="unit:5"/></game></save>')
        with self.assertRaises(UnsafeDeletion):
            remove_unit(xml, 'unit:5')

    @unittest.expectedFailure  # This fixture exposes cached self-closing spans, not a passing acceptance
    def test_self_closing_cached_settlement_preserves_unrelated_siblings(self):
        xml = (b'<save><game><map><tile id="tile:1">'
               b'<indianSettlement id="indianSettlement:5" owner="player:2"></indianSettlement>'
               b'</tile></map><cachedTile>'
               b'<indianSettlement id="indianSettlement:5" owner="player:2"/>'
               b'<indianSettlement id="indianSettlement:6" owner="player:3"></indianSettlement>'
               b'</cachedTile></game></save>')
        result = remove_settlement(xml, 'indianSettlement:5')
        ids = [e.get('id') for e in ET.fromstring(result).iter('indianSettlement')]
        self.assertEqual(ids, ['indianSettlement:6'])

if __name__ == '__main__':
    unittest.main()
