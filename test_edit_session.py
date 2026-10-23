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
