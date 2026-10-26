"""Offscreen behavioral checks for the extracted diplomacy view."""
import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication
from qt_readonly import QtExplorer
from qt_diplomacy_view import DiplomacyViewMixin


class DiplomacyViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_diplomacy_view_preserves_separate_categories(self):
        window = QtExplorer()
        try:
            self.assertIsInstance(window, DiplomacyViewMixin)
            self.assertEqual(set(window.diplomacy_grids), {"Rival Nations", "Natives"})
            self.assertEqual(window.diplomacy_tabs.count(), 2)
        finally:
            window.close()

    def test_diplomacy_control_staging(self):
        from xml.etree.ElementTree import fromstring
        from types import SimpleNamespace
        xml = (b'<save><player id="player:1"><stance player="player:2" value="peace"></stance>'
               b'<tension player="player:2" value="8"></tension></player>'
               b'<player id="player:2"><stance player="player:1" value="peace"></stance></player></save>')
        root = fromstring(xml)
        window = QtExplorer()
        try:
            window.document = SimpleNamespace(xml_bytes=xml,
                players={p.get('id'):p for p in root.iter('player')})
            with patch.object(window,'refresh_staged_view'), patch('qt_readonly.QMessageBox.warning') as warning:
                window.stage_relation('player:1','stance|player:2','alliance')
                window.stage_relation('player:1','tension|player:2','9')
            warning.assert_not_called()
            self.assertEqual(window.session.count, 2)
            self.assertEqual(window.session.edits[('player:1','stance|player:2')],('peace','alliance'))
        finally:
            window.session.exported_snapshot = dict(window.session.edits)
            window.close()

    def test_reciprocal_stance_directional_tension_and_safe_undo(self):
        from xml.etree.ElementTree import fromstring
        from types import SimpleNamespace
        from edit_preflight import preflight, unstage_checked
        xml = (b'<save><player id="player:1"><stance player="player:2" value="peace"/>'
               b'<tension player="player:2" value="8"/></player>'
               b'<player id="player:2"><stance player="player:1" value="peace"/>'
               b'<tension player="player:1" value="17"/></player></save>')
        root = fromstring(xml)
        window = QtExplorer()
        try:
            window.document = SimpleNamespace(
                xml_bytes=xml, players={p.get('id'): p for p in root.iter('player')})
            with patch.object(window, 'refresh_staged_view'), patch('qt_readonly.QMessageBox.warning') as warning:
                window.stage_relation('player:1', 'stance|player:2', 'war')
                window.stage_relation('player:1', 'tension|player:2', '29')
                window.stage_relation('player:2', 'stance|player:1', 'alliance')
                window.stage_relation('player:1', 'tension|player:3', '5')
            self.assertEqual(warning.call_count, 1)
            self.assertEqual(window.session.count, 2)
            result = fromstring(preflight(xml, window.session.edits))
            p1, p2 = list(result.iter('player'))
            self.assertEqual(p1.find('stance').get('value'), 'war')
            self.assertEqual(p2.find('stance').get('value'), 'war')
            self.assertEqual(p1.find('tension').get('value'), '29')
            self.assertEqual(p2.find('tension').get('value'), '17')
            unstage_checked(window.session, xml, ('player:1', 'stance|player:2'))
            self.assertEqual(window.session.count, 1)
            self.assertEqual(window.session.edits[('player:1','tension|player:2')], (8, 29))
        finally:
            window.session.exported_snapshot = dict(window.session.edits)
            window.close()

    def test_reciprocal_stance_visible_in_reverse_diplomacy_table(self):
        from types import SimpleNamespace
        from xml.etree.ElementTree import fromstring
        from PySide6.QtWidgets import QComboBox
        from qt_diplomacy import diplomacy_rows
        xml = (b'<save><player id="player:1" playerType="colonial" username="Denmark">'
               b'<stance player="player:2" value="peace"/></player>'
               b'<player id="player:2" playerType="colonial" username="Sweden">'
               b'<stance player="player:1" value="peace"/></player></save>')
        root = fromstring(xml)
        players = {p.get('id'): p for p in root.iter('player')}
        window = QtExplorer()
        try:
            window.document = SimpleNamespace(players=players, xml_bytes=xml)
            window.group = 'Diplomacy'
            with patch('qt_diplomacy_view.rows_for_scope',
                       side_effect=lambda doc, group, scope: diplomacy_rows(doc, 'player:2')):
                with patch.object(window, 'refresh_staged_view'):
                    window.stage_relation('player:1', 'stance|player:2', 'war')
                window.populate_diplomacy('')
            table = window.diplomacy_grids['Rival Nations']
            combos = table.findChildren(QComboBox, 'diplomacyStance')
            self.assertEqual(len(combos), 1)
            self.assertEqual(combos[0].currentData(), 'war')
            self.assertEqual(players['player:2'].find('stance').get('value'), 'peace')
        finally:
            window.session.exported_snapshot = dict(window.session.edits)
            window.close()

    def test_diplomacy_editor_replaces_cell_text_without_overlap(self):
        from types import SimpleNamespace
        from xml.etree.ElementTree import fromstring
        from qt_diplomacy import diplomacy_rows
        from PySide6.QtWidgets import QComboBox, QLineEdit
        xml = (b'<save><player id="player:1" playerType="colonial" username="Denmark">'
               b'<stance player="player:2" value="peace"/><tension player="player:2" value="0"/></player>'
               b'<player id="player:2" playerType="colonial" username="Sweden">'
               b'<stance player="player:1" value="peace"/></player></save>')
        root = fromstring(xml)
        window = QtExplorer()
        try:
            window.document = SimpleNamespace(players={p.get('id'):p for p in root.iter('player')},
                                               xml_bytes=xml)
            window.group = 'Diplomacy'
            with patch('qt_diplomacy_view.rows_for_scope',
                       side_effect=lambda doc, group, scope: diplomacy_rows(doc, 'player:1')):
                window.populate_diplomacy('')
            table = window.diplomacy_grids['Rival Nations']
            self.assertEqual(table.rowCount(), 1)
            self.assertEqual(table.item(0, 1).text(), '')
            self.assertEqual(table.item(0, 2).text(), '')
            self.assertIsNotNone(table.findChild(QComboBox, 'diplomacyStance'))
            self.assertIsNotNone(table.findChild(QLineEdit, 'diplomacyTension'))
            self.assertGreaterEqual(table.rowHeight(0), 40)
            self.assertGreaterEqual(table.columnWidth(1), 265)
        finally:
            window.close()

    def test_diplomacy_inspect_is_noop_outside_diplomacy(self):
        window = QtExplorer()
        try:
            for category in window.diplomacy_grids:
                self.assertIsNone(window.inspect_diplomacy(category))
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
