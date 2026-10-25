"""About dialog shows roadmap version and real line breaks."""
import os
import unittest
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication, QLabel
from qt_about_dialog import AboutDialog, APP_VERSION, BUILD_DATE, PROJECT_OWNER

class AboutDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_version_and_project_credit(self):
        dialog = AboutDialog()
        text = '\n'.join(w.text() for w in dialog.findChildren(QLabel))
        self.assertEqual(APP_VERSION, '0.6.2.6.4')
        self.assertIn('Qt Preview', text)
        self.assertIn(PROJECT_OWNER, text)
        self.assertIn(BUILD_DATE, text)
        self.assertNotIn('\\\\n', text)
        self.assertIn('READ ONLY', text)
        dialog.close()

if __name__ == '__main__':
    unittest.main()
