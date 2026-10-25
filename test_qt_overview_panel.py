"""Real offscreen regression for the Phase 1 graphical Overview panel."""
import os
import unittest
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
try:
    from PySide6.QtWidgets import QApplication, QLabel
    from qt_overview_panel import OverviewPanel, summary_parts
    from qt_property_icons import property_symbol, property_icon
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

    def test_colony_sections_render_with_all_values(self):
        panel = OverviewPanel()
        panel.setPlainText(
            'Christiansborg\nOwner: Danish\n'
            'Population and activity\nWorkplace workers: 6\n'
            'Largest warehouse stockpiles\nBells: 649\n'
            'Occupied buildings\nTown Hall: 1 worker')
        labels = [widget.text() for widget in panel.findChildren(QLabel)]
        for expected in ('Population and activity','Workplace workers',
                         'Largest warehouse stockpiles','Bells',
                         'Occupied buildings','Town Hall'):
            self.assertIn(expected, labels)
        panel.deleteLater()

    def test_icons_cover_property_rows(self):
        labels = ('Owner', 'Map location', 'Established', 'Liberty bells',
                  'Sons of Liberty', 'Production bonus', 'Workplace workers',
                  'Stationed units', 'Buildings', 'Stored goods types',
                  'Warehouse goods total', 'Bells', 'Crosses', 'Lumber',
                  'Ore', 'Muskets', 'Town Hall', 'Lumber Mill',
                  'Rum Distillery', 'Unknown custom building')
        for label in labels:
            with self.subTest(label=label):
                self.assertFalse(property_icon(label).isNull())
                self.assertFalse(property_icon(label).pixmap(19, 19).isNull())
        self.assertNotEqual(property_symbol('Muskets'), property_symbol('Bells'))
        self.assertNotEqual(property_symbol('Owner'), property_symbol('Ore'))

    def test_overview_widgets_include_property_icons(self):
        panel = OverviewPanel()
        panel.setPlainText('Christiansborg\\nOwner: Danish\\nLumber: 20')
        icons = [w for w in panel.findChildren(QLabel)
                 if w.toolTip() in ('Owner', 'Lumber')]
        self.assertEqual(len(icons), 2)
        self.assertTrue(all(not icon.pixmap().isNull() for icon in icons))
        panel.deleteLater()

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
