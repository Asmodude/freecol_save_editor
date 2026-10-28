"""OC-001: Qt progress editors and goods lists backed by a real .fsg container."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from PySide6.QtWidgets import QApplication, QFileDialog, QLineEdit
from qt_readonly import QtExplorer
from qt_navigation_lookup import find_navigation_item

_XML = b"""<savedGame><goods-type id="model.goods.bells"/>
<goods-type id="model.goods.crosses"/><goods-type id="model.goods.hammers"/>
<goods-type id="model.goods.tools"/>
<european-nation-type id="model.nationType.default">
<ability id="model.ability.electFoundingFather" value="true"/>
</european-nation-type>
<game id="game:1" turn="10">
<player id="player:1" playerType="colonial" nationType="model.nationType.default" ai="false" username="Human"
gold="100" tax="10" liberty="240" immigration="19" immigrationRequired="50"/>
<map><tile id="tile:1" x="1" y="1"><colony id="colony:1"
name="Christiansborg" owner="player:1" tile="tile:1">
<goodsContainer><storedGoods>
<goods type="model.goods.bells" amount="22"/>
<goods type="model.goods.crosses" amount="23"/>
<goods type="model.goods.hammers" amount="24"/>
<goods type="model.goods.tools" amount="25"/>
</storedGoods></goodsContainer></colony></tile></map></game></savedGame>"""


class SpecialResourcesQtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_owner_progress_and_liberty_stage_without_source_changes(self):
        with tempfile.TemporaryDirectory() as path:
            archive = Path(path) / 'source.fsg'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('savegame.xml', _XML)
            window = QtExplorer()
            try:
                with patch.object(QFileDialog, 'getOpenFileName', return_value=(str(archive), '')):
                    window.open_save()
                self.app.processEvents()
                text = window.overview.toPlainText()
                self.assertIn('Liberty Bells accumulated: 240', text)
                self.assertIn('Crosses needed for next immigrant to move to the docks in Europe: 50', text)
                editor = window.overview.findChild(QLineEdit, 'inlineLibertyInput')
                self.assertIsNotNone(editor)
                editor.setText('350')
                with patch.object(window, 'refresh_staged_view'):
                    editor.returnPressed.emit()
                self.assertEqual(window.session.edits[('player:1', 'liberty')], (240, 350))
                self.assertEqual(window.document.players['player:1'].get('liberty'), '240')
                with zipfile.ZipFile(archive) as z:
                    self.assertEqual(z.read('savegame.xml'), _XML)
                window.session.edits.clear()
                window.navigation.setCurrentItem(
                    find_navigation_item(window.navigation, 'National Goods', 'mine'))
                self.app.processEvents()
                self.assertEqual([e.get('id') for e in window.visible_rows],
                                 ['model.goods.tools'])
                window.navigation.setCurrentItem(
                    find_navigation_item(window.navigation, 'Colonies', 'mine'))
                self.app.processEvents()
                goods = window.colony_tables['Goods']
                editors = goods.findChildren(QLineEdit, 'colonyGoodsAmountInput')
                self.assertEqual([e.property('goodsTypeId') for e in editors],
                                 ['model.goods.tools'])
            finally:
                window.session.exported_snapshot = dict(window.session.edits)
                window.close()
                window.deleteLater()
                self.app.processEvents()


if __name__ == '__main__':
    unittest.main()
