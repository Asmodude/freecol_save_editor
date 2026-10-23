"""Safe read-only XML rendering for Qt inspector; never mutate SaveDocument XML."""
import xml.etree.ElementTree as ET
from xml.dom import minidom


def formatted_record_xml(element):
    if element is None:
        return ''
    raw = ET.tostring(element, encoding='unicode')
    return minidom.parseString(raw).toprettyxml(indent='  ')
