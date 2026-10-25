"""No comparison-mode switch remains after the single-table cutover."""
import os
import unittest
from unittest.mock import MagicMock, patch
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import qt_readonly


class DefaultWorkspaceTests(unittest.TestCase):
    def test_regular_launch_opens_one_model_view(self):
        fake_app = MagicMock()
        fake_app.exec.return_value = 0
        fake_window = MagicMock()
        with patch.object(qt_readonly, 'QApplication', return_value=fake_app), patch.object(
            qt_readonly, 'QtExplorer', return_value=fake_window
        ), patch.object(qt_readonly.sys, 'argv', ['qt_readonly.py']):
            self.assertEqual(qt_readonly.main(), 0)
        fake_window.show.assert_called_once()
        fake_window.set_model_view_comparison.assert_not_called()
