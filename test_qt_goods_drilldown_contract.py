"""Source-level regression checks for the Phase 1 nation-to-colony drill-down."""
from pathlib import Path
import unittest


class DrilldownContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=Path(__file__).with_name('qt_readonly.py').read_text(encoding='utf-8')
        cls.details=Path(__file__).with_name('qt_detail_tabs_view.py').read_text(encoding='utf-8')

    def test_drilldown_is_explicit_and_read_only(self):
        self.assertIn("self.jump_colony_button.clicked.connect(self.open_breakdown_colony)",self.source)
        self.assertIn("if section == 'By colony':",self.details)
        self.assertIn("self.navigation.setCurrentItem(destination)",self.source)
        self.assertIn("self.tabs.setCurrentWidget(table)",self.source)
        self.assertIn("if len(matches) != 1",self.source)
        self.assertIn("self.jump_colony_button.setEnabled(False)",self.source)
        self.assertNotIn("breakdown.selectRow(0)",self.source)
        self.assertIn("self.breakdown_target = None",self.source)
        self.assertIn("table.selectedItems()",self.details)
        self.assertIn("(-1 if section == 'By colony' else table.currentRow())",self.details)
        self.assertIn('self.tabs.currentChanged.connect(self.refresh_breakdown_action)',self.source)
        self.assertIn("table.cellClicked.connect(lambda row, column: self.inspect_detail('By colony'))",self.source)


_SAVE = b"""<?xml version="1.0"?><savedGame><game id="game:1" turn="10">
<player id="player:1" username="Human" nationId="model.nation.danish" playerType="colonial" ai="false" gold="100" tax="0"/>
<map width="4" height="4"><tile id="tile:1" x="1" y="1" type="model.tile.plains" owner="player:1">
 <colony id="colony:1" name="Christiansborg" owner="player:1" tile="tile:1">
  <goodsContainer id="gc:1"><storedGoods><goods type="model.goods.food" amount="120"/></storedGoods></goodsContainer>
 </colony></tile></map></game></savedGame>"""


class DrilldownBehaviourTests(unittest.TestCase):
    """Run the real Qt window offscreen; checks behaviour, not source text."""

    @classmethod
    def setUpClass(cls):
        import os
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
        try:
            from PySide6.QtWidgets import QApplication
        except ImportError:
            raise unittest.SkipTest('PySide6 not installed')
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        import tempfile, zipfile
        from PySide6.QtWidgets import QFileDialog
        import qt_readonly
        self.tmp = tempfile.TemporaryDirectory()
        path = Path(self.tmp.name) / 'drilldown.fsg'
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr('savegame.xml', _SAVE)
        self._original = QFileDialog.getOpenFileName
        QFileDialog.getOpenFileName = staticmethod(lambda *a, **k: (str(path), ''))
        self.window = qt_readonly.QtExplorer()
        self.window.show()  # isVisible() is only meaningful on a shown window
        self.window.open_save()
        self.app.processEvents()

    def tearDown(self):
        from PySide6.QtWidgets import QFileDialog
        QFileDialog.getOpenFileName = self._original
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.tmp.cleanup()

    def _select_nav(self, group):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QTreeWidgetItemIterator
        iterator = QTreeWidgetItemIterator(self.window.navigation)
        while iterator.value():
            item = iterator.value()
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(data, tuple) and data == (group, 'mine'):
                self.window.navigation.setCurrentItem(item)
                self.app.processEvents()
                return
            iterator += 1
        self.fail(f'navigation entry for {group} not found')

    def test_button_hidden_outside_national_goods_by_colony(self):
        self._select_nav('Colonies')
        self.assertFalse(self.window.jump_colony_button.isVisible())

    def test_drilldown_requires_explicit_row_and_opens_colony_goods(self):
        w = self.window
        self._select_nav('National Goods')
        food_row = next(r for r in range(w.grid.rowCount()) if w.grid.item(r, 0).text() == 'Food')
        w.grid.selectRow(food_row)
        self.app.processEvents()
        by_colony = w.colony_tables['By colony']
        w.tabs.setCurrentWidget(by_colony)
        self.app.processEvents()
        # Opening the tab is not a selection: visible but disabled.
        self.assertTrue(w.jump_colony_button.isVisible())
        self.assertFalse(w.jump_colony_button.isEnabled())
        by_colony.selectRow(0)
        self.app.processEvents()
        self.assertTrue(w.jump_colony_button.isEnabled())
        w.jump_colony_button.click()
        self.app.processEvents()
        self.assertEqual(w.navigation.currentItem().text(0), 'Christiansborg')
        goods = w.colony_tables['Goods']
        self.assertIs(w.tabs.currentWidget(), goods)
        self.assertEqual(goods.item(goods.currentRow(), 0).text(), 'Food')
        self.assertFalse(w.jump_colony_button.isVisible())


if __name__ == '__main__':
    unittest.main()
