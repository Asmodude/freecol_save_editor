"""Read-only goods art: local FreeCol images where found, vivid Qt fallback objects."""
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap, QPolygonF
from freecol_art_source import discover, read_bytes

GOODS = {
    'food': ('●','#ecb33a'), 'bells': ('♟','#e5b332'),
    'crosses': ('✝','#b794e8'), 'lumber': ('▥','#b97635'),
    'ore': ('◆','#7186a0'), 'muskets': ('⚔','#51637e'),
    'horses': ('♞','#ac6a38'), 'tools': ('⚒','#5f91c4'),
    'cotton': ('✿','#f6e8bc'), 'cloth': ('▤','#3e8fd0'),
    'sugar': ('◆','#f6cf78'), 'rum': ('◉','#bc7225'),
    'tobacco': ('❧','#49a05d'), 'cigars': ('▬','#99542e'),
    'coats': ('♜','#b34459'), 'silver': ('◆','#a4c8e4'),
    'fish': ('◆','#3c9cc6'), 'grain': ('♣','#dfbd44'),
    'hammers': ('⚒','#e09836'),
    'furs': ('◆','#a86c42'), 'tradegoods': ('▣','#cb8429'),
}
ALIASES = {'liberty bells':'bells', 'bells':'bells', 'crosses':'crosses',
           'trade goods':'tradegoods', 'trade_goods':'tradegoods'}
def goods_key(value):
    text = str(value or '').rsplit('.',1)[-1].strip().lower()
    return ALIASES.get(text,text) if text in GOODS or text in ALIASES else ''

class GoodsIcons:
    def __init__(self,source=None):
        self.source = discover() if source is None else source
        self.cache = {}

    def icon(self, value, size=22):
        key=goods_key(value)
        if not key:
            return QIcon()
        cache_key=(key,size)
        if cache_key in self.cache:
            return self.cache[cache_key]
        base,arc,prefix,_=self.source
        # Only exact resource names; do not accidentally use a different good.
        for path in (f'goods/{key}.png', f'goods/{key}.size0.png',
                     f'misc/goods/{key}.png'):
            data=read_bytes(base,arc,prefix,path)
            if data:
                pix=QPixmap()
                if pix.loadFromData(data) and not pix.isNull():
                    result=QIcon(pix)
                    self.cache[cache_key]=result
                    return result
        result=self._fallback(key,size)
        self.cache[cache_key]=result
        return result

    @staticmethod
    def _fallback(key,size):
        symbol,colour=GOODS[key]
        pix=QPixmap(size,size)
        pix.fill(Qt.GlobalColor.transparent)
        p=QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pigment=QColor(colour)
        p.setBrush(pigment)
        p.setPen(QPen(pigment.darker(170),max(1.0,size*.07)))
        # Transparent silhouettes, not square app badges.
        if key == 'furs':
            # Rich brown irregular hide, lighter inner fur and dark edge.
            p.drawPolygon(QPolygonF([QPointF(size*.13,size*.29),QPointF(size*.35,size*.12),
                QPointF(size*.49,size*.22),QPointF(size*.68,size*.10),
                QPointF(size*.89,size*.32),QPointF(size*.79,size*.49),
                QPointF(size*.87,size*.72),QPointF(size*.59,size*.86),
                QPointF(size*.41,size*.76),QPointF(size*.16,size*.85),
                QPointF(size*.20,size*.58)]))
            p.setBrush(QColor('#e7b77e'))
            p.setPen(QPen(QColor('#80512e'),max(1,size*.05)))
            p.drawEllipse(QRectF(size*.29,size*.32,size*.40,size*.35))
        elif key == 'tradegoods':
            # Cord-bound trading crate, not an unidentified placeholder.
            p.setBrush(QColor('#de9e46'))
            p.drawPolygon(QPolygonF([QPointF(size*.15,size*.32),QPointF(size*.57,size*.18),
                QPointF(size*.88,size*.34),QPointF(size*.46,size*.51)]))
            p.setBrush(QColor('#b66e2d'))
            p.drawPolygon(QPolygonF([QPointF(size*.15,size*.32),QPointF(size*.46,size*.51),
                QPointF(size*.46,size*.86),QPointF(size*.15,size*.66)]))
            p.setBrush(QColor('#edb45b'))
            p.drawPolygon(QPolygonF([QPointF(size*.46,size*.51),QPointF(size*.88,size*.34),
                QPointF(size*.88,size*.69),QPointF(size*.46,size*.86)]))
            p.setPen(QPen(QColor('#6d4825'),max(1,size*.055)))
            p.drawLine(QPointF(size*.68,size*.42),QPointF(size*.68,size*.77))
        elif key in ('lumber','cigars'):
            for i in range(3):
                p.drawRoundedRect(QRectF(size*.13,size*(.22+i*.20),size*.72,size*.15),
                                  size*.07,size*.07)
        elif key in ('rum','sugar'):
            p.drawRoundedRect(QRectF(size*.29,size*.12,size*.42,size*.73),size*.15,size*.12)
            p.fillRect(QRectF(size*.29,size*.36,size*.42,size*.12),QColor('#ffe69b'))
        elif key in ('ore','silver'):
            p.drawPolygon(QPolygonF([QPointF(size*.14,size*.69),QPointF(size*.31,size*.25),
                QPointF(size*.67,size*.17),QPointF(size*.88,size*.62),QPointF(size*.55,size*.84)]))
        elif key=='muskets':
            p.drawLine(QPointF(size*.15,size*.77),QPointF(size*.78,size*.18))
            p.drawLine(QPointF(size*.42,size*.69),QPointF(size*.80,size*.69))
        else:
            from PySide6.QtGui import QFont
            font=QFont('Segoe UI Symbol',max(10,int(size*.78)))
            font.setBold(True)
            p.setFont(font)
            p.drawText(QRectF(0,0,size,size),Qt.AlignmentFlag.AlignCenter,symbol)
        p.end()
        return QIcon(pix)
