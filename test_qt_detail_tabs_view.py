"""Behavioral coverage for extracted read-only detail tab view."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from xml.etree.ElementTree import fromstring

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication
from qt_readonly import QtExplorer
from qt_detail_tabs_view import DetailTabsMixin


class DetailTabsViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_empty_selection_has_only_overview_and_no_drilldown(self):
        window = QtExplorer()
        try:
            self.assertIsInstance(window, DetailTabsMixin)
            window.group = "Players"
            window.update_detail_tabs(None)
            self.assertEqual([window.tabs.tabText(i) for i in range(window.tabs.count())], ["Overview"])
            self.assertFalse(window.jump_unit_button.isVisible())
            self.assertFalse(window.jump_colony_button.isVisible())
        finally:
            window.close()

    def test_stationed_equipment_stages_by_identity_after_sorting(self):
        from PySide6.QtWidgets import QComboBox, QPushButton
        from PySide6.QtCore import Qt
        from xml.etree.ElementTree import tostring
        xml = (b'<save><specification><unit-type id="model.unit.freeColonist" movement="3">'
               b'<ability id="model.ability.canBeEquipped" value="true"/></unit-type>'
               b'<role id="model.role.default" maximum-count="1"/>'
               b'<role id="model.role.soldier" maximum-count="1"/>'
               b'<role id="model.role.dragoon" maximum-count="1">'
               b'<modifier id="model.modifier.movementBonus" type="additive" value="9"/>'
               b'</role></specification><game><player id="player:1"/>'
               b'<colony id="colony:1" owner="player:1" tile="tile:1">'
               b'<unit id="unit:1" unitType="model.unit.freeColonist" '
               b'owner="player:1" role="model.role.soldier" roleCount="1" movesLeft="3"/>'
               b'<unit id="unit:2" unitType="model.unit.freeColonist" '
               b'owner="player:1" role="model.role.default" roleCount="1" movesLeft="3"/>'
               b'</colony></game></save>')
        root = fromstring(xml)
        colony = next(root.iter('colony'))
        units = list(colony.iter('unit'))
        window = QtExplorer()
        try:
            window.document = SimpleNamespace(
                root=root, xml_bytes=xml, goods_types=[], units=units,
                unit_by_id=lambda uid: next((u for u in units if u.get('id') == uid), None),
                location_name=lambda key: str(key))
            window.group = 'Colonies'
            window.update_detail_tabs(colony)
            table = window.colony_tables['Stationed units']
            table.sortItems(0, Qt.SortOrder.DescendingOrder)
            combos = table.findChildren(QComboBox, 'stationedEquipmentRole')
            self.assertEqual(len(combos), 2)
            combo = next(e for e in combos if e.property('unitId') == 'unit:1')
            combo.setCurrentIndex(combo.findData('model.role.dragoon'))
            with patch.object(window, 'refresh_staged_view'):
                button = combo.parentWidget().findChild(QPushButton, 'stageStationedEquipment')
                button.click()
            self.assertEqual(window.session.edits[('unit:1','equipment')],
                             (('model.role.soldier',1),('model.role.dragoon',1)))
            self.assertNotIn(('unit:2','equipment'), window.session.edits)
            self.assertEqual(units[0].get('role'),'model.role.soldier')
        finally:
            window.session.exported_snapshot = dict(window.session.edits)
            window.close()

    def test_colony_worker_experience_can_be_staged_inline_by_unit_identity(self):
        window = QtExplorer()
        try:
            colony = fromstring(
                '<colony id="colony:1" owner="player:1" tile="tile:4">'
                '<building buildingType="model.building.townHall">'
                '<unit id="unit:7" unitType="model.unit.freeColonist" '
                'owner="player:1" experience="99" movesLeft="3"></unit>'
                '<unit id="unit:8" unitType="model.unit.freeColonist" '
                'owner="player:1" experience="12" movesLeft="3"></unit>'
                '</building></colony>')
            units = list(colony.findall('.//unit'))
            xml = (b'<save><game><player id="player:1"></player>' +
                   __import__('xml.etree.ElementTree', fromlist=['tostring']).tostring(colony) +
                   b'</game></save>')
            document = SimpleNamespace(
                units=units, goods_types=[], xml_bytes=xml,
                unit_by_id=lambda uid: next((u for u in units if u.get('id') == uid), None),
                location_name=lambda key: str(key))
            window.document = document
            window.group = 'Colonies'
            window.update_detail_tabs(colony)
            table = window.colony_tables['Workers']
            self.assertEqual(table.rowCount(), 2)
            from PySide6.QtWidgets import QLineEdit
            # Sort in reverse order; the callback must still bind unit:7.
            table.sortItems(4, __import__('PySide6.QtCore', fromlist=['Qt']).Qt.SortOrder.DescendingOrder)
            edit = next((e for e in table.findChildren(QLineEdit, 'workerExperienceInput')
                         if e.text() == '99'), None)
            self.assertIsNotNone(edit)
            edit.setText('120')
            with patch.object(window, 'refresh_staged_view'):
                edit.returnPressed.emit()
            self.assertEqual(window.session.edits[('unit:7', 'experience')], (99, 120))
            self.assertNotIn(('unit:8', 'experience'), window.session.edits)
            self.assertEqual(units[0].get('experience'), '99')
        finally:
            window.session.exported_snapshot = dict(window.session.edits)
            window.close()

    def test_staged_worker_refresh_preserves_workers_tab(self):
        window = QtExplorer()
        try:
            colony = fromstring(
                '<colony id="colony:1" owner="player:1" tile="tile:4">'
                '<building buildingType="model.building.townHall">'
                '<unit id="unit:7" unitType="model.unit.freeColonist" '
                'owner="player:1" experience="99" movesLeft="3"></unit>'
                '</building></colony>')
            units = list(colony.findall('.//unit'))
            from xml.etree.ElementTree import tostring
            xml = b'<save><game><player id="player:1"></player>' + tostring(colony) + b'</game></save>'
            document = SimpleNamespace(
                units=units, goods_types=[], xml_bytes=xml,
                unit_by_id=lambda uid: next((u for u in units if u.get('id') == uid), None),
                location_name=lambda key: str(key))
            window.document = document
            window.group = 'Colonies'
            window.selected_element = colony
            window.visible_rows = [colony]
            # Refresh invokes populate(), which needs standard navigation data.
            # Test the real click/refresh path using the same active-tab preservation.
            window.update_detail_tabs(colony)
            window.tabs.setCurrentWidget(window.colony_tables['Workers'])
            self.assertEqual(window.tabs.tabText(window.tabs.currentIndex()), 'Workers')
            with patch.object(window, 'populate', side_effect=lambda: window.tabs.setCurrentWidget(window.overview)), patch.object(window, 'inspect', side_effect=lambda: window.update_detail_tabs(colony)):
                window.refresh_staged_view()
            self.assertEqual(window.tabs.tabText(window.tabs.currentIndex()), 'Workers')
        finally:
            window.close()

    def test_native_skill_staging_retains_original(self):
        from xml.etree.ElementTree import fromstring
        from types import SimpleNamespace
        from unittest.mock import patch
        xml = (b'<save><game><map><tile><indianSettlement id="indianSettlement:1" lastTribute="0" convertProgress="0" learnableSkill="skill:a"/>'
               b'<indianSettlement id="indianSettlement:2" lastTribute="0" convertProgress="0" learnableSkill="skill:b"/></tile></map></game></save>')
        village = next(fromstring(xml).iter('indianSettlement'))
        window = QtExplorer()
        try:
            window.document = SimpleNamespace(
                xml_bytes=xml, professions=['skill:a','skill:b'],
                native_settlements=[village])
            window.overview.setPlainText('Village\nLearnable skill: Skill A')
            window.overview.set_record('Native settlements', village, window.document, window.session)
            from PySide6.QtWidgets import QComboBox, QPushButton
            combo = window.overview.findChild(QComboBox, 'nativeLearnableSkill')
            self.assertEqual(combo.count(), 2)
            combo.setCurrentIndex(combo.findData('skill:b'))
            with patch.object(window, 'refresh_staged_view'), patch('qt_readonly.QMessageBox.warning') as warning:
                window.overview.findChild(QPushButton, 'stageNativeLearnableSkill').click()
            warning.assert_not_called()
            self.assertEqual(window.session.edits[('indianSettlement:1','learnableSkill')],('skill:a','skill:b'))
            self.assertEqual(village.get('learnableSkill'), 'skill:a')
        finally:
            window.session.exported_snapshot = dict(window.session.edits)
            window.close()

    def test_alarm_edit_binds_real_player_and_skips_absent_record(self):
        from PySide6.QtWidgets import QLineEdit
        from PySide6.QtCore import Qt
        xml = (b'<save><game><player id="player:1" playerType="colonial" username="Same"/>'
               b'<player id="player:2" playerType="colonial" username="Same"/>'
               b'<map><tile><indianSettlement id="indianSettlement:1" lastTribute="0" '
               b'convertProgress="0"><alarm player="player:2" value="13"/></indianSettlement>'
               b'</tile></map></game></save>')
        root = fromstring(xml)
        village = next(root.iter('indianSettlement'))
        players = {p.get('id'): p for p in root.iter('player')}
        window = QtExplorer()
        try:
            window.document = SimpleNamespace(
                xml_bytes=xml, players=players, native_settlements=[village],
                units=[], unit_by_id=lambda uid: None,
                owner_name=lambda uid: uid, location_name=lambda tile: tile)
            window.group = 'Native settlements'
            window.update_detail_tabs(village)
            table = window.colony_tables['Alarm']
            self.assertEqual(table.rowCount(), 2)
            table.sortItems(0, Qt.SortOrder.DescendingOrder)
            editors = table.findChildren(QLineEdit, 'nativeSettlementAlarm')
            self.assertEqual(len(editors), 1)
            editor = editors[0]
            self.assertEqual(editor.property('relationshipKey'),
                             ('indianSettlement:1','alarm|player:2'))
            with patch.object(window, 'refresh_staged_view'), patch('qt_readonly.QMessageBox.warning') as warn:
                editor.setText('21')
                editor.returnPressed.emit()
            warn.assert_not_called()
            self.assertEqual(window.session.edits[
                ('indianSettlement:1','alarm|player:2')], (13,21))
            self.assertEqual(village.find('alarm').get('value'), '13')
        finally:
            window.session.exported_snapshot = dict(window.session.edits)
            window.close()

    def test_contextual_colony_button_disabled_outside_goods(self):
        window = QtExplorer()
        try:
            window.group = "Players"
            window.refresh_breakdown_action(0)
            self.assertFalse(window.jump_colony_button.isEnabled())
            self.assertFalse(window.jump_colony_button.isVisible())
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
