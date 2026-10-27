"""Manifest-grounded FreeCol unit artwork regression checks."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
import unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap
from qt_unit_icons import UnitIcons, authoritative_unit_type
from xml.etree.ElementTree import Element


class RoleArtworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_manifest_selects_distinct_specialist_and_role_art(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'resources'
            img = root / 'images'
            cases = [
                ('seasonedScout', 'scout', 'scout/seasonedScout'),
                ('veteranSoldier', 'soldier', 'soldier/veteranSoldier'),
                ('hardyPioneer', 'pioneer', 'pioneer/hardyPioneer'),
                ('freeColonist', 'dragoon', 'dragoon/dragoon'),
                ('jesuitMissionary', 'missionary', 'missionary/jesuitMissionary'),
                ('brave', 'default', 'civilian/brave'),
            ]
            lines = []
            for i, (unit, role, relative) in enumerate(cases):
                target = img / 'units' / (relative + '.png')
                target.parent.mkdir(parents=True, exist_ok=True)
                pix = QPixmap(8 + i, 8 + i)
                pix.fill()
                self.assertTrue(pix.save(str(target)))
                lines.append(f'image.unit.model.unit.{unit}.{role}=resources/images/units/{relative}.png')
            root.mkdir(parents=True, exist_ok=True)
            (root / 'resources.properties').write_text('\n'.join(lines), encoding='utf-8')
            icons = UnitIcons(source=(img, None, '', 'fixture'))
            for i, (unit, role, relative) in enumerate(cases):
                with self.subTest(unit=unit):
                    icon = icons.effective_icon('model.unit.' + unit, 'model.role.' + role)
                    self.assertFalse(icon.isNull())
                    self.assertEqual(icon.pixmap(100, 100).width(), 8 + i)

    def test_colony_unit_lists_use_authoritative_type_not_display_label(self):
        unit = Element('unit', {'id': 'unit:34400',
                                'unitType': 'model.unit.freeColonist'})
        self.assertEqual(authoritative_unit_type(unit, 'Free Colonist'),
                         'model.unit.freeColonist')
        self.assertEqual(authoritative_unit_type(None, 'Free Colonist'),
                         'Free Colonist')

    def test_missing_mapping_uses_type_fallback(self):
        icons = UnitIcons(source=(None, None, '', None))
        self.assertFalse(icons.effective_icon('model.unit.freeColonist',
                                             'model.role.scout').isNull())


if __name__ == '__main__':
    unittest.main()
