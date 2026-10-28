"""Read-only diagnosis of Founding Father factor in a FreeCol .fsg.

Usage: py tools/diagnose_founding_father_factor.py "C:\\path\\save.fsg"
Prints only relevant specification paths/options, never player information.
"""
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

TARGET = 'model.option.foundingFatherFactor'

def inspect(path):
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read('savegame.xml'))
    specs = list(root.iter('specification'))
    print('Specification nodes:', len(specs))
    for index, spec in enumerate(specs):
        print('Specification', index, 'attributes:', dict(spec.attrib))
    parents = {child: parent for parent in root.iter() for child in parent}
    matches = [node for node in root.iter() if node.get('id') == TARGET]
    print('Founding Father factor nodes:', len(matches))
    for node in matches:
        lineage = []
        current = node
        while current is not None:
            if current.tag in ('specification', 'optionGroup', 'integerOption'):
                lineage.append(current.tag + ':' + str(current.get('id', '')) +
                               (' [value=' + str(current.get('value')) + ']' if current.get('value') is not None else ''))
            current = parents.get(current)
        print(' > '.join(reversed(lineage)))
    print('No archive data changed.')

if __name__ == '__main__':
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_file():
        raise SystemExit('Usage: py tools/diagnose_founding_father_factor.py <save.fsg>')
    inspect(sys.argv[1])
