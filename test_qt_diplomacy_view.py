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

    def test_diplomacy_inspect_is_noop_outside_diplomacy(self):
        window = QtExplorer()
        try:
            for category in window.diplomacy_grids:
                self.assertIsNone(window.inspect_diplomacy(category))
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
