"""Read-only XML inspector regression."""
import unittest
from xml.etree.ElementTree import fromstring, tostring
from qt_raw_xml import formatted_record_xml


class RawXmlTests(unittest.TestCase):
    def test_nested_record_is_pretty_and_unchanged(self):
        element=fromstring('<colony id="colony:7"><building buildingType="fort"><unit id="unit:3"/></building></colony>')
        before=tostring(element)
        display=formatted_record_xml(element)
        self.assertIn('colony:7',display)
        self.assertIn('unit:3',display)
        self.assertIn('\n  <building',display)
        self.assertEqual(tostring(element),before)

    def test_escapes_special_characters(self):
        element=fromstring('<unit id="a&amp;b"/>')
        self.assertIn('a&amp;b',formatted_record_xml(element))
        self.assertEqual(formatted_record_xml(None),'')


if __name__=='__main__':
    unittest.main()
