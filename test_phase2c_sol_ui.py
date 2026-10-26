import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from xml.etree.ElementTree import fromstring
from PySide6.QtWidgets import QApplication, QLineEdit
from qt_readonly import QtExplorer
from edit_preflight import preflight

XML = (b'<save><game><colony id="colony:1" owner="player:1" liberty="100" sonsOfLiberty="25" '
       b'oldSonsOfLiberty="25" tories="2" oldTories="2" productionBonus="0">'
       b'<unit id="unit:1"></unit><unit id="unit:2"></unit></colony></game></save>')

class SoLUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_eligible_colony_stages_target_and_recomputes_six_fields(self):
        window = QtExplorer()
        try:
            root = fromstring(XML)
            colony = next(root.iter("colony"))
            window.document = SimpleNamespace(colonies=[colony], xml_bytes=XML)
            window.overview.setPlainText("Colony\nSons of Liberty: 25")
            window.overview.set_record("Colonies", colony, window.document, window.session)
            field = window.overview.findChild(QLineEdit, "inlineSonsoflibertytargetInput")
            self.assertIsNotNone(field)
            self.assertIn("recalculate on export", field.toolTip())
            field.setText("50")
            with patch.object(window,"refresh_staged_view"):
                field.returnPressed.emit()
            self.assertEqual(window.session.edits[("colony:1","sonsOfLibertyTarget")],(25,50))
            after = next(fromstring(preflight(XML,window.session.edits)).iter("colony"))
            self.assertEqual(colony.get("sonsOfLiberty"), "25")
            self.assertEqual(after.get("sonsOfLiberty"), "50")
            self.assertEqual(after.get("liberty"), "200")
            self.assertEqual(after.get("oldSonsOfLiberty"), "50")
            self.assertEqual(after.get("productionBonus"), "1")
            self.assertEqual(after.get("tories"), "1")
            self.assertEqual(after.get("oldTories"), "1")
        finally:
            window.session.exported_snapshot = dict(window.session.edits)
            window.close()

if __name__=="__main__":
    unittest.main()
