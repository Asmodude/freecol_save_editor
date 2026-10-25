"""Offscreen Phase 1 flag and goods rendering regressions."""
import os
import unittest
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
try:
    from PySide6.QtWidgets import QApplication
    from qt_flag_icons import flag_pixmap, RATIOS
    from qt_goods_icons import GoodsIcons, goods_key, GOODS
except ImportError:
    QApplication = None

@unittest.skipUnless(QApplication is not None,'PySide6 unavailable')
class VisualAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])

    def test_flags_are_rectangular_and_use_national_proportions(self):
        for name,(w,h) in RATIOS.items():
            with self.subTest(name=name):
                pix=flag_pixmap('model.nation.'+name,28)
                self.assertFalse(pix.isNull())
                self.assertEqual(pix.height(),28)
                self.assertEqual(pix.width(),round(28*w/h))
                self.assertGreater(pix.width(),pix.height())

    def test_danish_flag_has_off_centre_cross(self):
        image=flag_pixmap('model.nation.danish',28).toImage()
        self.assertGreater(image.pixelColor(1,1).red(),150)
        self.assertGreater(image.pixelColor(17,1).green(),200)
        self.assertGreater(image.pixelColor(17,13).green(),200)

    def test_portuguese_flag_has_red_green_and_blue(self):
        im=flag_pixmap('model.nation.portuguese',60).toImage()
        self.assertGreater(im.pixelColor(3,4).green(),im.pixelColor(3,4).red())
        self.assertGreater(im.pixelColor(im.width()-3,4).red(),im.pixelColor(im.width()-3,4).green())
        self.assertTrue(any(im.pixelColor(x,y).blue()>im.pixelColor(x,y).red()*1.3
                        for x in range(30,55) for y in range(20,48)))

    def test_all_goods_have_visible_art_without_local_install(self):
        icons=GoodsIcons(source=(None,None,'','unavailable'))
        for good in GOODS:
            with self.subTest(good=good):
                pix=icons.icon(good,24).pixmap(24,24)
                self.assertFalse(pix.isNull())
                self.assertTrue(any(pix.toImage().pixelColor(x,y).alpha()>0
                                    for x in range(24) for y in range(24)))
        self.assertEqual(goods_key('model.goods.muskets'),'muskets')
        self.assertEqual(goods_key('Unknown item'),'')
        self.assertEqual(goods_key('model.goods.furs'),'furs')
        self.assertEqual(goods_key('Trade Goods'),'tradegoods')
        self.assertEqual(goods_key('model.goods.tradeGoods'),'tradegoods')

    def test_furs_and_trade_goods_have_distinct_painted_icons(self):
        icons=GoodsIcons(source=(None,None,'','unavailable'))
        for name in ('Furs','Trade Goods'):
            with self.subTest(name=name):
                image=icons.icon(name,32).pixmap(32,32).toImage()
                self.assertTrue(any(image.pixelColor(x,y).alpha()>0
                                    for x in range(32) for y in range(32)))
        fur=icons.icon('Furs',32).pixmap(32,32).toImage()
        trade=icons.icon('Trade Goods',32).pixmap(32,32).toImage()
        self.assertNotEqual(fur.pixelColor(16,16).name(),trade.pixelColor(16,16).name())

if __name__=='__main__':
    unittest.main()
