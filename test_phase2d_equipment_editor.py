"""2D-1 equipment editor consistency across Overview and Stationed units."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import unittest
from types import SimpleNamespace
from xml.etree.ElementTree import fromstring
from PySide6.QtWidgets import QApplication
from edit_session import EditSession
from qt_equipment_editor import EquipmentEditor


class SharedEquipmentEditorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.root = fromstring(
            '<save><role id="model.role.default" maximum-count="1"/>'
            '<role id="model.role.pioneer" maximum-count="5"/>'
            '<role id="model.role.soldier" maximum-count="1"/>'
            '<unit-type id="model.unit.hardyPioneer" movement="3">'
            '<ability id="model.ability.canBeEquipped" value="true"/></unit-type>'
            '<player id="player:1"/>'
            '<unit id="unit:9" unitType="model.unit.hardyPioneer" owner="player:1"'
            ' role="model.role.default" roleCount="0" movesLeft="3"/></save>'
        )
        self.doc = SimpleNamespace(root=self.root)
        self.unit = next(self.root.iter('unit'))
        self.session = EditSession()

    def test_both_contexts_share_role_labels_natural_pioneer_and_stage_values(self):
        for context in ('overview', 'stationed'):
            with self.subTest(context=context):
                widget = EquipmentEditor(self.doc, self.unit, self.session, context=context)
                try:
                    self.assertEqual(widget.selector.currentData(), 'model.role.pioneer')
                    self.assertEqual(widget.count.value(), 5)
                    self.assertEqual(widget.tools_label.text(), '100 tools')
                    self.assertEqual(widget.button.text(), 'Stage Change')
                    self.assertEqual(widget.status.text(), 'Not staged')
                    observed = []
                    widget.stage_requested.connect(lambda *args: observed.append(args))
                    widget.button.click()
                    self.assertEqual(observed, [('unit:9', 'model.role.pioneer', 5)])
                finally:
                    widget.deleteLater()

    def test_default_role_uses_zero_count(self):
        widget = EquipmentEditor(self.doc, self.unit, self.session)
        try:
            widget.selector.setCurrentIndex(widget.selector.findData('model.role.default'))
            self.assertEqual(widget.count.value(), 0)
            self.assertEqual(widget.tools_label.text(), 'No equipment')
        finally:
            widget.deleteLater()


if __name__ == '__main__':
    unittest.main()
