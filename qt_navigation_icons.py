"""Qt navigation artwork. Original vector UI glyphs; never ships FreeCol assets.

Known European flags are drawn from simple geometric colour fields. Local FreeCol
nation imagery is only loaded from exact, unambiguous matches; a native nation
without a verified emblem gets a neutral initial medallion instead.
"""
from pathlib import Path
import re

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPen, QPixmap

from freecol_art_source import discover, read_bytes


EUROPEAN_FLAGS = {
    'danish': 'denmark', 'english': 'england', 'french': 'france',
    'spanish': 'spain', 'dutch': 'netherlands', 'portuguese': 'portugal',
    'swedish': 'sweden', 'russian': 'russia',
}
GLYPHS = {
    'overview': '≡', 'diplomacy': '⚖', 'colonies': '⌂',
    'colony': '⌂', 'units': '♞', 'ships': '⚓',
    'goods': '▤', 'research': '◉', 'fathers': '♜',
    'options': '⚙', 'map': '◇', 'section': '▦',
    'settlements': '⌂', 'nation': '✦', 'planned': '◇',
    'field': '⌖',
}


def nation_key(nation_id):
    """Extract a whole FreeCol nation identifier; never substring-match tribes."""
    value = (nation_id or '').rsplit('.', 1)[-1].strip().lower()
    return value if re.fullmatch(r'[a-z][a-z0-9_-]*', value) else ''


def _paint_flag(p, name, size):
    """Draw recognisable historical European national flags without external art."""
    w = size
    def rect(x, y, width, height, color):
        p.fillRect(QRectF(x*w, y*w, width*w, height*w), QColor(color))
    if name == 'denmark':
        rect(0, 0, 1, 1, '#c8102e'); rect(.31, 0, .14, 1, '#fff'); rect(0, .43, 1, .14, '#fff')
    elif name == 'sweden':
        rect(0, 0, 1, 1, '#006aa7'); rect(.31, 0, .14, 1, '#fecc00'); rect(0, .43, 1, .14, '#fecc00')
    elif name == 'england':
        rect(0, 0, 1, 1, '#fff'); rect(.42, 0, .16, 1, '#ce1124'); rect(0, .42, 1, .16, '#ce1124')
    elif name in ('france', 'netherlands', 'russia', 'spain'):
        colors = {
            'france': ('#0055a4', '#fff', '#ef4135'),
            'netherlands': ('#ae1c28', '#fff', '#21468b'),
            'russia': ('#fff', '#0039a6', '#d52b1e'),
            'spain': ('#aa151b', '#f1bf00', '#aa151b'),
        }[name]
        for i, color in enumerate(colors):
            if name == 'france':
                rect(i/3, 0, 1/3, 1, color)
            elif name == 'spain':
                y, h = ((0, .25), (.25, .5), (.75, .25))[i]
                rect(0, y, 1, h, color)
            else:
                rect(0, i/3, 1, 1/3, color)
    elif name == 'portugal':
        rect(0, 0, .4, 1, '#006600'); rect(.4, 0, .6, 1, '#ff0000')
        p.setBrush(QColor('#ffcc33')); p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QRectF(.31*w, .35*w, .25*w, .3*w))


class NavigationIcons:
    def __init__(self):
        self._cache = {}
        self._source = discover()

    def _local_nation_image(self, key):
        # Only explicit locations whose *whole filename* identifies the nation.
        # Never take a fuzzy hit: flags for neighbouring nations must not mix.
        base, archive, prefix, _ = self._source
        for relative in (f'misc/flags/{key}.png', f'misc/flags/{key}.size0.png',
                         f'nations/{key}.png', f'misc/nations/{key}.png'):
            data = read_bytes(base, archive, prefix, relative)
            if data:
                pixmap = QPixmap()
                if pixmap.loadFromData(data) and not pixmap.isNull():
                    return QIcon(pixmap)
        return None

    def icon(self, kind='section', nation_id=None, native=False, size=20):
        key = nation_key(nation_id)
        cache_key = (kind, key, native, size)
        if cache_key in self._cache:
            return self._cache[cache_key]
        # Prefer the installation's actual artwork when it is unambiguously named.
        local = self._local_nation_image(key) if key and kind == 'nation' else None
        if local:
            self._cache[cache_key] = local
            return local
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        flag = EUROPEAN_FLAGS.get(key) if not native and kind == 'nation' else None
        if flag:
            _paint_flag(p, flag, size)
            p.setPen(QPen(QColor('#64748b'), .6))
            p.drawRect(QRectF(.5, .5, size-1, size-1))
        else:
            background = '#e4edf8' if not native else '#efe5d6'
            foreground = '#2d5278' if not native else '#775532'
            p.setBrush(QColor(background))
            p.setPen(QPen(QColor('#a8b8ca' if not native else '#c3aa85'), 1))
            p.drawRoundedRect(QRectF(1, 1, size-2, size-2), 5, 5)
            symbol = key[:2].upper() if native and key else GLYPHS.get(kind, '·')
            font = QFont('Segoe UI Symbol', max(8, int(size * (.39 if len(symbol)>1 else .65))))
            font.setBold(True)
            p.setFont(font)
            p.setPen(QColor(foreground))
            p.drawText(QRectF(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, symbol)
        p.end()
        result = QIcon(pix)
        self._cache[cache_key] = result
        return result
