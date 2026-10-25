"""Correct-aspect European flag icons, created without bundled game artwork."""
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QColor, QIcon, QImage, QPainter, QPen, QPixmap, QPolygonF

from qt_navigation_icons import flag_for_nation

# Widely recognised civil-flag proportions. European heraldry on Portugal's
# flag is deliberately simplified at navigation sizes but retained at 48px.
RATIOS = {'denmark': (37, 28), 'sweden': (16, 10),
          'england': (5, 3), 'france': (3, 2),
          'netherlands': (3, 2), 'russia': (3, 2),
          'spain': (3, 2), 'portugal': (3, 2)}


def flag_pixmap(nation_id, height=16):
    name = flag_for_nation(nation_id)
    if not name:
        return QPixmap()
    width = round(height * RATIOS[name][0] / RATIOS[name][1])
    # Supersampling gives cleaner heraldic details at 16px.
    scale = 3
    w, h = width * scale, height * scale
    image = QImage(w, h, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    p = QPainter(image)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    def fill(x, y, a, b, colour):
        p.fillRect(QRectF(x*w, y*h, a*w, b*h), QColor(colour))
    if name in ('denmark', 'sweden'):
        fill(0,0,1,1, '#c8102e' if name=='denmark' else '#006aa7')
        colour = '#ffffff' if name=='denmark' else '#fecc00'
        # Danish official 12:4:12 vertically, 12:4:21 horizontally.
        if name == 'denmark':
            fill(12/37,0,4/37,1,colour); fill(0,12/28,1,4/28,colour)
        else:
            fill(5/16,0,2/16,1,colour); fill(0,4/10,1,2/10,colour)
    elif name == 'england':
        fill(0,0,1,1,'#ffffff')
        fill(0.42,0,.16,1,'#ce1124');fill(0,.405,1,.19,'#ce1124')
    elif name in ('france','netherlands','russia'):
        bands = {
          'france': ('#0055a4','#ffffff','#ef4135'),
          'netherlands': ('#ae1c28','#ffffff','#21468b'),
          'russia': ('#ffffff','#0039a6','#d52b1e')}[name]
        for i,colour in enumerate(bands):
            if name == 'france': fill(i/3,0,1/3,1,colour)
            else: fill(0,i/3,1,1/3,colour)
    elif name == 'spain':
        fill(0,0,1,1,'#aa151b');fill(0,.25,1,.5,'#f1bf00')
    elif name == 'portugal':
        fill(0,0,.4,1,'#006600');fill(.4,0,.6,1,'#ff0000')
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor('#e8b731'),max(1.4,h*.032)))
        p.drawEllipse(QRectF(w*.28,h*.20,w*.32,h*.60))
        p.drawLine(QPointF(w*.30,h*.5),QPointF(w*.59,h*.5))
        p.setBrush(QColor('#ffffff'))
        p.setPen(QPen(QColor('#bd1e2d'),max(1,h*.022)))
        p.drawPolygon(QPolygonF([
            QPointF(w*.363,h*.33),QPointF(w*.518,h*.33),
            QPointF(w*.518,h*.61),QPointF(w*.44,h*.73),
            QPointF(w*.363,h*.61)]))
        p.setBrush(QColor('#174a96'));p.setPen(Qt.PenStyle.NoPen)
        for x,y in ((.421,.39),(.389,.49),(.438,.49),(.488,.49),(.421,.60)):
            p.drawEllipse(QRectF(w*x,h*y,w*.019,h*.047))
    p.end()
    return QPixmap.fromImage(image).scaled(
        width,height,Qt.AspectRatioMode.IgnoreAspectRatio,
        Qt.TransformationMode.SmoothTransformation)


def flag_icon(nation_id, height=16):
    pix = flag_pixmap(nation_id,height)
    return QIcon(pix) if not pix.isNull() else QIcon()
