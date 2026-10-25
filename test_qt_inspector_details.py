"""Inspector parser and actual offscreen read-only widget regression."""
import os
import unittest
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from qt_inspector_details import inspector_fields

class InspectorParserTests(unittest.TestCase):
    def test_fields_and_notes(self):
        fields, notes = inspector_fields('Name: Christiansborg\nOwner: Danish\n\nFull unit attributes\nNo saved entry.')
        self.assertEqual(fields, [('Name','Christiansborg'), ('Owner','Danish')])
        self.assertEqual(notes, ['Full unit attributes', 'No saved entry.'])

    def test_preserves_values_containing_colons(self):
        self.assertEqual(inspector_fields('Saved value: 12:30')[0], [('Saved value','12:30')])

try:
    from PySide6.QtWidgets import QApplication, QLabel
    from qt_inspector_details import InspectorDetails
except ImportError:
    QApplication = None

@unittest.skipUnless(QApplication is not None, 'PySide6 required')
class InspectorWidgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_repeated_updates_and_clear(self):
        widget = InspectorDetails()
        for n in range(8):
            source = f'Name: Colony {n}\nGold: {n}'
            widget.setPlainText(source)
            self.assertEqual(widget.toPlainText(), source)
            self.assertIn(f'Colony {n}', [w.text() for w in widget.findChildren(QLabel)])
        widget.clear()
        self.assertEqual(widget.toPlainText(), '')
        widget.deleteLater()

if __name__ == '__main__':
    unittest.main()
