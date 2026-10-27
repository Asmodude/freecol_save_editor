"""Phase 2D-1: effective equipment roles prefer real artwork and never fabricate sprites."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QPixmap
from qt_unit_icons import UnitIcons


class RoleArtworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_role_artwork_is_used_when_present(self):
        icons = UnitIcons(source=(None, None, '', None))
        image = QPixmap(10, 10)
        image.fill()
        from PySide6.QtCore import QBuffer, QIODevice
        buf = QBuffer()
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buf, 'PNG')
        data = bytes(buf.data())
        with patch.object(icons, '_local_image', return_value=data) as local:
            icon = icons.effective_icon('model.unit.freeColonist', 'model.role.pioneer')
            self.assertFalse(icon.isNull())
            local.assert_called_once_with('pioneer')

    def test_missing_role_art_reverts_to_type_with_role(self):
        icons = UnitIcons(source=(None, None, '', None))
        with patch.object(icons, '_local_image', return_value=None), \
             patch.object(icons, 'icon', return_value=QIcon()) as fallback:
            icons.effective_icon('model.unit.freeColonist', 'model.role.scout')
            fallback.assert_called_once_with('model.unit.freeColonist', size=23, role='model.role.scout')


if __name__ == '__main__':
    unittest.main()
