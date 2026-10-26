"""Safe read-only XML rendering for Qt inspector; never mutate SaveDocument XML."""
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom

_ATTRIBUTE = re.compile(r'([\w:.-]+="[^"]*")')
_OPENING_TAG = re.compile(r'^(\s*)<([\w:.-]+)((?:\s+[\w:.-]+="[^"]*")+)(/?>)$')


def formatted_record_xml(element):
    if element is None:
        return ''
    raw = ET.tostring(element, encoding='unicode')
    pretty = minidom.parseString(raw).toprettyxml(indent='  ')
    lines = []
    for line in pretty.splitlines():
        match = _OPENING_TAG.fullmatch(line)
        if match is None:
            lines.append(line)
            continue
        margin, tag, attributes, ending = match.groups()
        attrs = _ATTRIBUTE.findall(attributes)
        if len(attrs) < 2:
            lines.append(line)
            continue
        lines.append(margin + '<' + tag)
        lines.extend(margin + '  ' + attr for attr in attrs)
        lines.append(margin + ending)
    return '\n'.join(lines) + '\n'
