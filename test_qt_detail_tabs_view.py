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
