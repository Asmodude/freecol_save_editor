import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from xml.etree.ElementTree import fromstring
from PySide6.QtWidgets import QApplication, QLineEdit
from qt_readonly import QtExplorer

class ColonyGoodsUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_goods_id_survives_sort_and_absent_good_can_be_created(self):
        window = QtExplorer()
        try:
            xml = (b'<save><goods-type id="model.goods.food"></goods-type>'
                   b'<goods-type id="model.goods.tools"></goods-type>'
                   b'<colony id="colony:1" owner="player:1"><goodsContainer><storedGoods>'
                   b'<goods type="model.goods.food" amount="30"></goods>'
                   b'</storedGoods></goodsContainer></colony></save>')
            root = fromstring(xml)
            colony = next(root.iter("colony"))
            window.group = "Colonies"
            window.document = SimpleNamespace(colonies=[colony], goods_types=["model.goods.food","model.goods.tools"],
                xml_bytes=xml, units=[], root=root, unit_by_id=lambda uid: None,
                location_name=lambda value: str(value))
            window.update_detail_tabs(colony)
            table = window.colony_tables["Goods"]
            table.sortItems(0)
            edits = table.findChildren(QLineEdit, "colonyGoodsAmountInput")
            tools = next(field for field in edits if field.property("goodsTypeId") == "model.goods.tools")
            food = next(field for field in edits if field.property("goodsTypeId") == "model.goods.food")
            self.assertEqual(tools.text(), "0")
            with patch.object(window, "refresh_staged_view"):
                tools.setText("90")
                tools.returnPressed.emit()
                food.setText("45")
                food.returnPressed.emit()
            self.assertEqual(window.session.edits[("colony:1","model.goods.tools")], (0,90))
            self.assertEqual(window.session.edits[("colony:1","model.goods.food")], (30,45))
            self.assertEqual(colony.find(".//goods").get("amount"), "30")
        finally:
            window.session.exported_snapshot = dict(window.session.edits)
            window.close()

if __name__ == "__main__":
    unittest.main()
