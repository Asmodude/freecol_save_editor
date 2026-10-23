"""Native settlement affiliation is not a colony-worker relationship."""
import unittest
from types import SimpleNamespace
from xml.etree.ElementTree import fromstring
from qt_settlement_details import settlement_units


class SettlementUnitsTests(unittest.TestCase):
    def test_home_and_owned_units_without_colony_workers(self):
        village=fromstring('<indianSettlement id="indianSettlement:1" owner="player:2"><ownedUnits id="unit:7"/></indianSettlement>')
        units=[
            fromstring('<unit id="unit:6" owner="player:2" indianSettlement="indianSettlement:1" unitType="model.unit.brave"/>'),
            fromstring('<unit id="unit:7" owner="player:2" unitType="model.unit.brave"/>'),
            fromstring('<unit id="unit:8" owner="player:3" indianSettlement="indianSettlement:1"/>'),
            fromstring('<unit id="unit:9" owner="player:2" indianSettlement="indianSettlement:elsewhere"/>')
        ]
        doc=SimpleNamespace(units=units,location_name=lambda k:k or '')
        headers,rows=settlement_units(village,doc)
        self.assertEqual([row[0] for row in rows],['unit:6','unit:7'])
        self.assertEqual(headers[2],'Current location')

    def test_empty_affiliation(self):
        village=fromstring('<indianSettlement id="indianSettlement:1" owner="player:2"/>')
        doc=SimpleNamespace(units=[],location_name=lambda k:k or '')
        self.assertEqual(settlement_units(village,doc)[1],[])


if __name__=='__main__':
    unittest.main()
