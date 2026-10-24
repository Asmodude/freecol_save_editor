"""Presentation-only property glyphs for the read-only Qt Overview.

No game facts are inferred. All displayed properties retain the saved values.
Icons are original simple Qt drawings, not bundled FreeCol artwork.
"""
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPen, QPixmap

# Keys match the labels produced by qt_overview.record_overview. Every row,
# including dynamically named goods and occupied buildings, gets an icon.
PROPERTY_ICONS = {
    'Owner': ('♛', '#4565a5'), 'Map location': ('⌖', '#2f8a79'),
    'Established': ('◷', '#9464a3'), 'Liberty bells': ('♪', '#c18b12'),
    'Sons of Liberty': ('✦', '#a16d2e'), 'Production bonus': ('↑', '#43895a'),
    'Workplace workers': ('♟', '#926f52'), 'Stationed units': ('✚', '#ba4540'),
    'Buildings': ('⌂', '#b9792b'), 'Stored goods types': ('▤', '#8a7b4e'),
    'Warehouse goods total': ('▣', '#a87532'),
    'Gold': ('●', '#c19718'), 'Tax': ('%', '#af6540'),
    'Score': ('★', '#8270b5'), 'Colonies': ('⌂', '#b9792b'),
    'Native settlements': ('◇', '#587f50'),
    'Nation': ('⚑', '#4f769e'), 'Type': ('▦', '#64728c'),
    'Location': ('⌖', '#2f8a79'), 'Learnable skill': ('✦', '#688c4b'),
    'Role': ('♟', '#926f52'), 'Experience': ('★', '#8270b5'),
    'Moves left': ('➜', '#408d9a'), 'State': ('◈', '#596d95'),
    'Status': ('◈', '#596d95'), 'FreeCol identifier': ('#', '#697480'),
}
GOODS = {
    'Bells': ('♪', '#cb9a17'), 'Crosses': ('✝', '#a289be'),
    'Lumber': ('▥', '#977141'), 'Ore': ('◆', '#6f7890'),
    'Muskets': ('✚', '#ac4743'), 'Food': ('●', '#6f9d4c'),
    'Cotton': ('✿', '#7592ba'), 'Tobacco': ('❧', '#719253'),
    'Sugar': ('◇', '#b79356'), 'Tools': ('⚒', '#6f7784'),
    'Horses': ('♞', '#9d6d3b'), 'Cloth': ('▤', '#7384ab'),
    'Coats': ('♜', '#92667a'), 'Rum': ('◉', '#a66a31'),
    'Cigars': ('▬', '#8c6541'), 'Silver': ('◆', '#7d8d9d'),
}
# Occupied-building names come from the save and can differ by ruleset.
BUILDING_HINTS = {
    'town hall': ('⌂', '#9b7952'), 'lumber mill': ('▥', '#99703a'),
    'rum distillery': ('◉', '#a66a31'), 'weaver': ('▤', '#7788b6'),
    'school': ('▣', '#5d85a4'), 'church': ('✝', '#937ab2'),
    'blacksmith': ('⚒', '#727a85'), 'warehouse': ('▣', '#a87532'),
    'dock': ('⚓', '#398ca6'), 'stable': ('♞', '#947244'),
}


def property_symbol(label):
    """Return symbol and palette for any visible property, without altering it."""
    if label in PROPERTY_ICONS:
        return PROPERTY_ICONS[label]
    if label in GOODS:
        return GOODS[label]
    if label.startswith('Wanted goods'):
        return ('▤', '#a87532')
    lowered = label.casefold()
    for name, style in BUILDING_HINTS.items():
        if name in lowered:
            return style
    return ('•', '#758493')


def property_icon(label, size=19):
    symbol, hue = property_symbol(label)
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    colour = QColor(hue)
    painter.setPen(QPen(colour.darker(115), max(.8, size * .055)))
    painter.setBrush(colour.lighter(143))
    painter.drawRoundedRect(QRectF(1, 1, size-2, size-2), size*.27, size*.27)
    painter.setPen(colour.darker(170))
    font = QFont('Segoe UI Symbol', max(8, int(size*.62)))
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(QRectF(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, symbol)
    painter.end()
    return QIcon(pixmap)
