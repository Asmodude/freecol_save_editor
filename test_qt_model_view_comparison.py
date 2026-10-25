"""Single table: the model/view workspace is the default and sole table."""
import os
import unittest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication
from qt_readonly import QtExplorer


class SingleWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_only_model_view_is_installed(self):
        window = QtExplorer()
        try:
            window.show()
            self.app.processEvents()
            self.assertTrue(window.model_view.isVisible())
            self.assertFalse(hasattr(window, 'grid'))
            self.assertFalse(hasattr(window, 'set_model_view_comparison'))
            self.assertIs(window.model_view.model(), window.record_proxy)
        finally:
            window.close()
