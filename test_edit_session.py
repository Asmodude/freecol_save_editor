"""Phase 0 EditSession contract; no GUI or actual user save required."""
import unittest
import xml.etree.ElementTree as ET
from edit_session import EditSession, EditValidationError


class EditSessionTests(unittest.TestCase):
    def setUp(self):
        self.session=EditSession()

    def test_stage_and_revert_to_original(self):
        key=('player:1','gold')
        self.session.stage(key,10,12)
        self.assertEqual(self.session.edits[key],(10,12))
        self.assertEqual(self.session.count,1)
        self.assertEqual(self.session.staged_value(key,10),12)
        self.session.stage(key,10,10)
        self.assertEqual(self.session.count,0)

    def test_numeric_limits(self):
        for field, maximum in (('tax',100),('sonsOfLibertyTarget',100),('experience',200),('gold',2147483647)):
            key=('player:1',field)
            self.assertEqual(self.session.validate(key,str(maximum),original=0),maximum)
            with self.assertRaisesRegex(EditValidationError,'maximum is'):
                self.session.validate(key,str(maximum+1),original=0)

    def test_bad_numeric_inputs_are_rejected(self):
        for invalid in ('-1','12.3','  ','١٢','1e2'):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(EditValidationError,'Invalid quantity'):
                    self.session.validate(('player:1','gold'),invalid,original=0)

    def test_choice_lists(self):
        self.assertEqual(self.session.validate(('player:1','stance|player:2'),'cease_fire',original='war'),'cease_fire')
        self.assertEqual(self.session.validate(('indianSettlement:1','learnableSkill'),'model.unit.expertFarmer',
                      original='x',professions=['model.unit.expertFarmer']),'model.unit.expertFarmer')
        with self.assertRaisesRegex(EditValidationError,'Invalid choice'):
            self.session.validate(('player:1','stance|player:2'),'neutral',original='war')

    def test_movement_cap_and_missing_rules_fail_closed(self):
        root=ET.fromstring("""<save><specification>
          <unit-type id="model.unit.freeColonist" movement="3"/>
          <role id="model.role.default"/>
          </specification><game><player id="player:1"/></game></save>""")
        unit=ET.Element('unit',{'id':'unit:1','unitType':'model.unit.freeColonist',
                                'role':'model.role.default','owner':'player:1'})
        key=('unit:1','movesLeft')
        self.assertEqual(self.session.validate(key,'3',original=0,root=root,units=[unit]),3)
        with self.assertRaisesRegex(EditValidationError,'maximum is 3'):
            self.session.validate(key,'4',original=0,root=root,units=[unit])
        with self.assertRaisesRegex(EditValidationError,'Movement edit unavailable'):
            self.session.validate(key,'1',original=0,root=root,units=[])

    def test_delete_stage_keys_remain_compatible(self):
        self.session.stage_unit_deletion('unit:7')
        self.session.stage_native_unit_deletion('unit:8','indianSettlement:9')
        self.session.stage_settlement_deletion('indianSettlement:10')
        self.assertEqual(self.session.edits[('unit:7','deleteUnit')],('present','delete'))
        self.assertEqual(self.session.edits[('unit:8|indianSettlement:9','deleteNativeUnit')],('present','delete'))
        self.assertEqual(self.session.edits[('indianSettlement:10','deleteSettlement')],('present','delete'))

    def test_equipment_refuses_staged_deletion_before_rule_validation(self):
        self.session.stage_unit_deletion('unit:7')
        unit=ET.Element('unit',{'id':'unit:7'})
        with self.assertRaisesRegex(ValueError,'already staged for deletion'):
            self.session.stage_equipment(ET.Element('game'),unit,'model.role.pioneer',1)

    def test_save_as_never_overwrites_original_or_existing_target(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'original.fsg'
            source.write_bytes(b'not a real save')
            target=Path(directory)/'other.fsg'
            target.write_bytes(b'existing file')
            with self.assertRaisesRegex(ValueError,'cannot overwrite'):
                self.session.save_as(source,source)
            with self.assertRaisesRegex(ValueError,'never overwrites'):
                self.session.save_as(source,target)
            self.assertEqual(source.read_bytes(),b'not a real save')
            self.assertEqual(target.read_bytes(),b'existing file')

    def test_unstage_and_clear(self):
        self.session.stage(('unit:1','experience'),0,10)
        self.assertTrue(self.session.is_changed(('unit:1','experience')))
        self.session.unstage(('unit:1','experience'))
        self.assertFalse(self.session.is_changed(('unit:1','experience')))
        self.session.stage(('unit:1','experience'),0,5)
        self.session.clear()
        self.assertEqual(list(self.session.items()),[])


if __name__=='__main__':
    unittest.main()
