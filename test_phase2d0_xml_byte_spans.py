"""Phase 2D-0 M1 locator regression: structural and hostile XML byte boundaries."""
import unittest
from xml.etree import ElementTree as ET
from xml_byte_spans import element_spans, spans_for_id, UnsafeXMLSpan


class XMLByteSpansTests(unittest.TestCase):
    def test_each_element_slice_matches_original_tree(self):
        xml = (b'<save><game><tile id="tile:1" note="a>b" other="x/y">'
               b'<unit id="unit:1"/>'
               b'<unit id="unit:2" note="> /"><unit id="unit:3" /></unit>'
               b'<!-- <unit id="unit:404"/> -->'
               b'<![CDATA[<unit id="unit:405"/>]]>'
               b'</tile><tile id="tile:2"><unit id="unit:4"></unit></tile>'
               b'</game></save>')
        root = ET.fromstring(xml)
        nodes = {(): root}
        def add(parent, path):
            for i, child in enumerate(parent):
                nodes[path + (i,)] = child
                add(child, path + (i,))
        add(root, ())
        spans = element_spans(xml)
        self.assertEqual(len(spans), len(nodes))
        for path, tag, attrs, start, end in spans:
            slice_root = ET.fromstring(xml[start:end])
            expected = nodes[path]
            self.assertEqual(slice_root.tag, expected.tag)
            self.assertEqual(slice_root.attrib, expected.attrib)
            self.assertEqual(len(list(slice_root.iter())), len(list(expected.iter())))
        self.assertEqual(len(spans_for_id(xml, 'unit', 'unit:1')), 1)
        self.assertEqual(len(spans_for_id(xml, 'unit', 'unit:3')), 1)
        self.assertNotIn('unit:404', [attrs.get('id') for _, _, attrs, _, _ in spans])

    def test_self_closing_before_parent_end(self):
        xml = b'<save><unit id="unit:5"/></save>'
        span = spans_for_id(xml, 'unit', 'unit:5')[0]
        self.assertEqual(xml[span[0]:span[1]], b'<unit id="unit:5"/>')

    def test_repeated_cached_id_kept_distinct(self):
        xml = (b'<save><indianSettlement id="indianSettlement:5"/>'
               b'<cached><indianSettlement id="indianSettlement:5"></indianSettlement></cached></save>')
        matched = spans_for_id(xml, 'indianSettlement', 'indianSettlement:5')
        self.assertEqual(len(matched), 2)
        self.assertNotEqual(matched[0], matched[1])

    def test_refuse_unsupported_xml(self):
        for xml in (b'<!DOCTYPE save><save/>',
                    b'<?xml version="1.0" encoding="ISO-8859-1"?><save/>',
                    b'<save><ns:unit xmlns:ns="urn:test"/></save>',
                    b'<save><unit id="a"></save>',
                    b'<save>\x00</save>'):
            with self.subTest(xml=xml), self.assertRaises(UnsafeXMLSpan):
                element_spans(xml)

    def test_missing_identifier_refused(self):
        with self.assertRaises(UnsafeXMLSpan):
            spans_for_id(b'<save/>', 'unit', 'unit:999')


if __name__ == '__main__':
    unittest.main()
