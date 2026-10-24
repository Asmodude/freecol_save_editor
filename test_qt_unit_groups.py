"""Unit group filters preserve identity and complete ownership coverage."""
import unittest
from types import SimpleNamespace
from xml.etree.ElementTree import fromstring
from qt_unit_groups import unit_groups,unit_group_scope,scoped_units


class UnitGroupTests(unittest.TestCase):
    def test_partition_without_loss_and_preserve_parent_list(self):
        colony=fromstring('<colony id="colony:1" tile="tile:1" owner="p"><building><unit id="worker"/></building></colony>')
        units=[fromstring(x) for x in (
            '<unit id="worker" owner="p" unitType="model.unit.freeColonist"/>',
            '<unit id="u1" owner="p" location="colony:1"/>',
            '<unit id="ship" owner="p" unitType="model.unit.merchantman"/>',
            '<unit id="passenger" owner="p" location="ship"/>',
            '<unit id="out" owner="p" location="tile:999"/>',
            '<unit id="rival" owner="enemy" location="colony:1"/>')]
        doc=SimpleNamespace(units=units,colonies=[colony])
        groups=unit_groups(doc,'p')
        self.assertEqual({u.get('id') for u in groups[('colony','colony:1')]},{'worker','u1'})
        self.assertEqual([u.get('id') for u in groups[('ship','')]],['passenger'])
        self.assertEqual({u.get('id') for u in groups[('other','')]},{'ship','out'})
        self.assertEqual(sum(map(len,groups.values())),5)
        self.assertEqual(scoped_units(doc,unit_group_scope('p','colony','colony:1')),groups[('colony','colony:1')])
        self.assertEqual(scoped_units(doc,unit_group_scope('enemy','colony','colony:1')),[])
        self.assertEqual(scoped_units(doc,'unit-group|p|unknown|'),[])


if __name__=='__main__':
    unittest.main()
