"""Read-only unit artwork from the user's installed FreeCol graphics.

No copyrighted assets are bundled. Exact unit-type filenames only; unknown
types receive an unmistakably neutral fallback instead of fabricated sprites.
"""
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap, QPolygonF
from freecol_art_source import discover, read_bytes


def unit_key(value):
    value = str(value or '').rsplit('.', 1)[-1].strip()
    if ' ' in value:
        words = value.split()
        value = words[0].lower() + ''.join(w[:1].upper() + w[1:] for w in words[1:])
    return value if value and value.replace('_', '').isalnum() else ''


class UnitIcons:
    def __init__(self, source=None):
        self.source = discover() if source is None else source
        self.cache = {}

    def icon(self, value, size=23):
        key = unit_key(value)
        if not key:
            return QIcon()
        cache_key = (key, size)
        if cache_key in self.cache:
            return self.cache[cache_key]
        base, archive, prefix, _ = self.source
        # FreeCol installation layout varies between versions/rulesets.
        for relative in (f'units/{key}.png', f'units/{key}.size0.png',
                         f'unit/{key}.png', f'misc/units/{key}.png'):
            data = read_bytes(base, archive, prefix, relative)
            if data:
                pix = QPixmap()
                if pix.loadFromData(data) and not pix.isNull():
                    result = QIcon(pix)
                    self.cache[cache_key] = result
                    return result
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor('#b67b46'))
        painter.setPen(QPen(QColor('#503f35'), max(1, size * .07)))
        painter.drawEllipse(QRectF(size*.34, size*.10, size*.32, size*.27))
        painter.drawPolygon(QPolygonF([
            QPointF(size*.29, size*.42),
            QPointF(size*.70, size*.42),
            QPointF(size*.79, size*.86),
            QPointF(size*.20, size*.86)]))
        painter.end()
        result = QIcon(pix)
        self.cache[cache_key] = result
        return result
