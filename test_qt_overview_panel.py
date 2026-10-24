"""Real offscreen regression for the Phase 1 graphical Overview panel."""
import os
import unittest
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
try:
    from PySide6.QtWidgets import QApplication, QLabel
    from qt_overview_panel import OverviewPanel, summary_parts
except ImportError:
    QApplication = None

@unittest.skipUnless(QApplication is not None, 'PySide6 unavailable')
class OverviewPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_summary_fields_and_notes(self):
        title, fields, notes = summary_parts(
            'Christiansborg\n\nOwner: Danish\nLiberty bells: 42\n'
            'Population and activity\nBuildings: 3\n')
        self.assertEqual(title, 'Christiansborg')
        self.assertEqual(fields, [('Owner','Danish'),('Liberty bells','42'),('Buildings','3')])
        self.assertIn('Population and activity', notes)

    def test_repeated_updates_and_read_only_text(self):
        panel = OverviewPanel()
        for i in range(12):
            expected = f'Colony {i}\nOwner: Danish\nBuildings: {i}'
            panel.setPlainText(expected)
            self.assertEqual(panel.toPlainText(), expected)
            self.assertTrue(any(x.text() == f'Colony {i}' for x in panel.findChildren(QLabel)))
        panel.clear()
        self.assertEqual(panel.toPlainText(), '')
        panel.deleteLater()

if __name__ == '__main__':
    unittest.main()
