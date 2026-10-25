"""Preview command-line flag is opt-in and never alters the default Qt UI."""
import os
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import qt_readonly


class PreviewFlagTests(unittest.TestCase):
    def _launch(self, arguments):
        fake_app = MagicMock()
        fake_app.exec.return_value = 0
        fake_window = MagicMock()
        with patch.object(qt_readonly, "QApplication", return_value=fake_app), patch.object(
            qt_readonly, "QtExplorer", return_value=fake_window
        ), patch.object(qt_readonly.sys, "argv", ["qt_readonly.py", *arguments]):
            self.assertEqual(qt_readonly.main(), 0)
        fake_window.show.assert_called_once()
        return fake_window

    def test_default_launch_keeps_accepted_table(self):
        window = self._launch([])
        window.set_model_view_comparison.assert_not_called()

    def test_preview_launch_explicitly_enables_new_table(self):
        window = self._launch(["--compare-model-view"])
        window.set_model_view_comparison.assert_called_once_with(True)


if __name__ == "__main__":
    unittest.main()
