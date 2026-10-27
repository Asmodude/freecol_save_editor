"""Behavioural regression for Claude review M1/M2: source truth and stage-key markers."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from xml.etree.ElementTree import Element
from PySide6.QtWidgets import QApplication, QTableWidgetItem
from PySide6.QtCore import Qt

from qt_readonly import QtExplorer
from qt_role_markers import equipment_marker


class ReviewCorrectionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_marker_matrix_all_equipment_transitions_and_undo(self):
        for source_role, pending, expected in (
            ('model.role.pioneer', True, 'staged'),  # 100 -> 80, same role
            ('model.role.dragoon', True, 'staged'),  # dragoon -> default
            ('model.role.default', True, 'staged'),  # default -> soldier
            ('model.role.dragoon', False, 'equipped'),  # undo
            ('model.role.default', False, None),
        ):
            with self.subTest(source_role=source_role, pending=pending):
                self.assertEqual(equipment_marker(source_role, pending), expected)

    def test_player_source_details_exclude_staged_gold_and_tax(self):
        window = QtExplorer()
        try:
            player = Element('player', {'id':'player:1', 'username':'Denmark',
                'gold':'7225', 'tax':'12', 'playerType':'european'})
            window.document = SimpleNamespace()
            window.group = 'Players'
            window.visible_rows = [player]
            window.session.stage(('player:1','gold'), '7225', '9999')
            window.session.stage(('player:1','tax'), '12', '20')
            with patch('qt_readonly.selected_source_record', return_value=player), \
                 patch.object(window, 'update_detail_tabs'), \
                 patch('qt_readonly.record_overview', return_value='Player overview'), \
                 patch.object(window.overview, 'set_record'):
                window.inspect()
            details = window.details.toPlainText()
            self.assertIn('Gold: 7225', details)
            self.assertIn('Tax: 12', details)
            self.assertNotIn('9999', details)
            self.assertNotIn('Tax: 20', details)
        finally:
            window.session.exported_snapshot = dict(window.session.edits)
            window.close()

    def test_diplomacy_source_details_exclude_staged_stance_and_tension(self):
        window = QtExplorer()
        try:
            relation = Element('relation', {'owner':'player:1','other':'player:2',
                'nation':'Dutch', 'stance':'peace', 'tension':'8'})
            window.group = 'Diplomacy'
            window.document = SimpleNamespace(players={'player:1':Element('player')})
            table = window.diplomacy_grids['Rival Nations']
            table.setRowCount(1)
            item = QTableWidgetItem('Dutch')
            item.setData(Qt.ItemDataRole.UserRole, relation)
            table.setItem(0, 0, item)
            table.selectRow(0)
            window.session.stage(('player:1', 'stance|player:2'), 'peace', 'war')
            window.session.stage(('player:1', 'tension|player:2'), '8', '29')
            window.inspect_diplomacy('Rival Nations')
            details = window.details.toPlainText()
            self.assertIn('Stance: peace', details)
            self.assertIn('Tension: 8', details)
            self.assertNotIn('Stance: war', details)
            self.assertNotIn('Tension: 29', details)
        finally:
            window.session.exported_snapshot = dict(window.session.edits)
            window.close()


if __name__ == '__main__':
    unittest.main()
