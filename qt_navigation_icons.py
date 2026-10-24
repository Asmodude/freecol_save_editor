"""Qt navigation artwork. Original vector UI glyphs; never ships FreeCol assets.

Known European flags are drawn from simple geometric colour fields. Local FreeCol
nation imagery is only loaded from exact, unambiguous matches; a native nation
without a verified emblem gets a decorative, non-historical symbol instead.
"""
import re

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPen, QPixmap, QPolygonF

from freecol_art_source import discover, read_bytes


EUROPEAN_FLAGS = {
    'danish': 'denmark', 'denmark': 'denmark',
    'english': 'england', 'england': 'england',
    'french': 'france', 'france': 'france',
    'spanish': 'spain', 'spain': 'spain',
    'dutch': 'netherlands', 'netherlands': 'netherlands',
    'portuguese': 'portugal', 'portugal': 'portugal',
    'swedish': 'sweden', 'sweden': 'sweden',
    'russian': 'russia', 'russia': 'russia',
}
GLYPHS = {
    'overview': '▤', 'diplomacy': '⚖', 'colonies': '⌂',
    'colony': '⌂', 'units': '✚', 'ships': '⚓',
    'goods': '◆', 'research': '◉', 'fathers': '♜',
    'options': '⚙', 'map': '◈', 'section': '▦',
    'settlements': '⌂', 'nation': '♛', 'planned': '◇',
    'field': '⌖',
}
# Distinct hues by function. Native medallions are decorative UI symbols, not
# purportedly authentic heraldry. Use the same fallback for an unknown tribe.
ICON_PALETTE = {
    'overview': ('#e1edfa', '#255eac'),
    'diplomacy': ('#eee6fc', '#7145a3'),
    'colonies': ('#fff0d1', '#a45f12'),
    'colony': ('#fff0d1', '#a45f12'),
    'units': ('#fce2de', '#b33224'),
    'ships': ('#dff2fa', '#176b93'),
    'goods': ('#ffefd0', '#ad710d'),
    'research': ('#dcf2fa', '#137a9c'),
    'fathers': ('#efe3d3', '#765127'),
    'options': ('#e6e9ed', '#536174'),
    'map': ('#dcefe4', '#237b68'),
    'section': ('#e8e9f8', '#495e9c'),
    'settlements': ('#e8f0d5', '#587d28'),
    'nation': ('#fff0c7', '#986816'),
    'planned': ('#ebedf0', '#7c8796'),
    'field': ('#e6eaf1', '#50647e'),
}
NATIVE_STYLES = {
    'iroquois': (0, '#56864a'), 'tupi': (1, '#ad7530'),
    'sioux': (2, '#407fa2'), 'arawak': (3, '#b05766'),
    'apache': (4, '#6a6b9e'), 'inca': (5, '#bd8c20'),
    'aztec': (6, '#548e83'), 'cherokee': (7, '#916447'),
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


def _paint_native_emblem(p, key, size):
    """Distinct abstract motifs, never faux historical tribal insignia."""
    motif, colour = NATIVE_STYLES.get(key, (8, '#897658'))
    w = size
    p.setBrush(QColor('#f6efd9'))
    p.setPen(QPen(QColor(colour), 1.4))
    p.drawEllipse(QRectF(w*.07, w*.07, w*.86, w*.86))
    p.setPen(QPen(QColor(colour), max(1.3, w*.085)))
    cx, cy = w*.5, w*.5
    if motif % 3 == 0:
        p.drawEllipse(QRectF(w*.33,w*.33,w*.34,w*.34))
        for dx,dy in ((0,-.29),(0,.29),(-.29,0),(.29,0)):
            p.drawLine(QPointF(cx+dx*w*.55,cy+dy*w*.55),
                       QPointF(cx+dx*w,cy+dy*w))
    elif motif % 3 == 1:
        p.drawLine(QPointF(w*.27,w*.72), QPointF(w*.5,w*.25))
        p.drawLine(QPointF(w*.5,w*.25), QPointF(w*.73,w*.72))
        p.drawLine(QPointF(w*.28,w*.57), QPointF(w*.72,w*.57))
    else:
        for y in (.32,.48,.64):
            p.drawLine(QPointF(w*.28,w*y), QPointF(w*.72,w*y))
        p.drawEllipse(QRectF(w*.43,w*.15,w*.14,w*.14))


def flag_for_nation(nation_id):
    """Exact alias matching; no guessing from prefixes such as 'port'."""
    return EUROPEAN_FLAGS.get(nation_key(nation_id))


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
        # Draw known national flags ourselves: an unrelated local nation sprite must
        # never override a recognised flag (notably Portugal's green/red).
        known_flag = flag_for_nation(nation_id) if not native and kind == 'nation' else None
        local = self._local_nation_image(key) if key and kind == 'nation' and not known_flag else None
        if local:
            self._cache[cache_key] = local
            return local
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        flag = flag_for_nation(nation_id) if not native and kind == 'nation' else None
        if flag:
            _paint_flag(p, flag, size)
            p.setPen(QPen(QColor('#64748b'), .6))
            p.drawRect(QRectF(.5, .5, size-1, size-1))
        elif native and kind == 'nation' and key:
            _paint_native_emblem(p, key, size)
        else:
            background, foreground = ICON_PALETTE.get(kind, ICON_PALETTE['section'])
            p.setBrush(QColor(background))
            p.setPen(QPen(QColor(foreground).lighter(140), 1))
            p.drawRoundedRect(QRectF(1, 1, size-2, size-2), 5, 5)
            symbol = GLYPHS.get(kind, '·')
            font = QFont('Segoe UI Symbol', max(8, int(size * .65)))
            font.setBold(True)
            p.setFont(font)
            p.setPen(QColor(foreground))
            p.drawText(QRectF(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, symbol)
        p.end()
        result = QIcon(pix)
        self._cache[cache_key] = result
        return result
