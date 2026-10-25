"""Offscreen tests for extracted Founding Fathers view component."""
import os
import unittest
from xml.etree.ElementTree import Element

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication, QLabel
from qt_readonly import QtExplorer
from qt_founding_fathers_view import FoundingFathersViewMixin


class FoundingFathersViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_view_is_composed_into_explorer(self):
        self.assertTrue(issubclass(QtExplorer, FoundingFathersViewMixin))

    def test_missing_portrait_is_handled_without_error(self):
        window = QtExplorer()
        try:
            label = QLabel()
            window._set_father_portrait(label, "unknown-father-id", 60, 60)
            self.assertEqual(label.text(), 'Portrait unavailable')
        finally:
            window.close()

    def test_no_recruiting_father_is_safe(self):
        window = QtExplorer()
        try:
            window.recruiting_father = None
            self.assertIsNone(window.inspect_recruiting_father())
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
