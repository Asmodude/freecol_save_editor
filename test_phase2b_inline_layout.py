"""Phase 2B accepted layout: inline Overview, right-side staged review."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import unittest
from types import SimpleNamespace
from xml.etree.ElementTree import Element
from PySide6.QtWidgets import QApplication, QSplitter, QLineEdit
from qt_readonly import QtExplorer
from qt_overview_panel import OverviewPanel


class InlineLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_review_is_inside_right_pane_not_window_bottom_dock(self):
        window = QtExplorer()
        try:
            self.assertIsInstance(window.right_splitter, QSplitter)
            self.assertIs(window.right_splitter.widget(1), window.pending_panel)
            self.assertEqual(window.right_splitter.orientation().name, 'Vertical')
            self.assertFalse(hasattr(window, 'pending_dock'))
        finally:
            window.close()

    def test_inline_gold_control_captures_original_player_id(self):
        window = QtExplorer()
        try:
            player = Element('player', {'id': 'player:1', 'username': 'Denmark',
                                        'gold': '7225', 'tax': '10'})
            doc = SimpleNamespace(players={'player:1': player})
            window.document = doc
            captured = []
            window.overview.edit_requested.connect(
                lambda rid, field, value: captured.append((rid, field, value)))
            window.overview.setPlainText('Denmark\nGold: 7225\nTax: 10')
            window.overview.set_record('Players', player, doc, window.session)
            editor = window.overview.findChild(QLineEdit, 'inlineGoldInput')
            self.assertIsNotNone(editor)
            editor.setText('9000')
            editor.returnPressed.emit()
            self.assertEqual(captured, [('player:1', 'gold', '9000')])
            self.assertEqual(player.get('gold'), '7225')
            self.assertIn('76A9E8', editor.styleSheet())
        finally:
            window.close()

    def test_native_gold_does_not_become_editable(self):
        window = QtExplorer()
        try:
            native = Element('player', {'id': 'player:2', 'gold': '-2147483648'})
            doc = SimpleNamespace(players={'player:2': native})
            window.overview.setPlainText('Native\nGold: N/A')
            window.overview.set_record('Players', native, doc, window.session)
            self.assertIsNone(window.overview.findChild(QLineEdit, 'inlineGoldInput'))
        finally:
            window.close()


if __name__ == '__main__':
    unittest.main()
