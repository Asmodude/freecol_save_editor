import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from xml.etree.ElementTree import fromstring
from PySide6.QtWidgets import QApplication, QComboBox, QSpinBox, QLabel, QPushButton
from qt_readonly import QtExplorer

class PioneerUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
    def test_hardy_pioneer_natural_role_and_tools(self):
        explorer = QtExplorer()
        try:
            xml = (b'<save><unit-type id="model.unit.hardyPioneer" movement="3">'
                   b'<ability id="model.ability.canBeEquipped" value="true"></ability></unit-type>'
                   b'<role id="model.role.default" maximum-count="1"></role>'
                   b'<role id="model.role.pioneer" maximum-count="5"></role>'
                   b'<player id="player:1"></player>'
                   b'<unit id="unit:9" unitType="model.unit.hardyPioneer" owner="player:1" '
                   b'role="model.role.default" roleCount="0" movesLeft="3"></unit></save>')
            root = fromstring(xml)
            unit = next(root.iter('unit'))
            explorer.document = SimpleNamespace(root=root, xml_bytes=xml, unit_by_id=lambda uid: unit)
            explorer.overview.setPlainText('Hardy Pioneer\nRole: Default')
            explorer.overview.set_record('Units', unit, explorer.document, explorer.session)
            selector = explorer.overview.findChild(QComboBox, 'unitEquipmentRole')
            amount = explorer.overview.findChild(QSpinBox, 'unitEquipmentCount')
            tools = explorer.overview.findChild(QLabel, 'pioneerToolQuantity')
            self.assertEqual(selector.currentData(), 'model.role.pioneer')
            self.assertEqual(amount.maximum(), 5)
            self.assertEqual(tools.text(), '100 tools')
            self.assertEqual(amount.value(), 5)
            self.assertEqual(explorer.session.count, 0)
            amount.setValue(4)
            self.assertEqual(tools.text(), '80 tools')
            with patch.object(explorer, 'refresh_staged_view'):
                explorer.overview.findChild(QPushButton, 'stageUnitEquipment').click()
            self.assertEqual(explorer.session.edits[('unit:9','equipment')],
                             (('model.role.default',0),('model.role.pioneer',4)))
            self.assertEqual(unit.get('role'), 'model.role.default')
        finally:
            explorer.session.exported_snapshot = dict(explorer.session.edits)
            explorer.close()

if __name__ == '__main__':
    unittest.main()
