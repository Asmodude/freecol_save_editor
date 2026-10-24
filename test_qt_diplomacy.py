"""Diplomacy is exact saved state: absent entries are never inferred."""
import unittest
from types import SimpleNamespace
from xml.etree.ElementTree import fromstring
from qt_diplomacy import diplomacy_rows,settlement_alarm_rows

class DiplomacyTests(unittest.TestCase):
    def test_players_and_absence(self):
        a=fromstring('<player id="a" playerType="colonial"><stance player="b" value="war"/><tension player="b" value="34"/></player>')
        b=fromstring('<player id="b" username="France" playerType="colonial"/>')
        n=fromstring('<player id="n" username="Arawak" playerType="indian"/>')
        doc=SimpleNamespace(players={'a':a,'b':b,'n':n})
        rows=diplomacy_rows(doc,'a')
        self.assertEqual([(r.get('nation'),r.get('kind'),r.get('value')) for r in rows],
                         [('France','stance','war'),('France','tension','34'),('Arawak','stance','(absent)'),('Arawak','tension','(absent)')])
        self.assertEqual(diplomacy_rows(doc,'missing'),[])
        self.assertEqual(a.find('stance').get('value'),'war')

    def test_alarm_only_colonial_players(self):
        c=fromstring('<player id="c" username="Denmark" playerType="colonial"/>')
        n=fromstring('<player id="n" username="Arawak" playerType="indian"/>')
        settlement=fromstring('<indianSettlement><alarm player="c" value="45"/></indianSettlement>')
        doc=SimpleNamespace(players={'c':c,'n':n})
        self.assertEqual(settlement_alarm_rows(doc,settlement),[('Denmark','45')])
        settlement.clear()
        self.assertEqual(settlement_alarm_rows(doc,settlement),[('Denmark','(absent)')])

if __name__=='__main__':
    unittest.main()
