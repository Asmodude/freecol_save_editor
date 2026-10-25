"""Read-only graphical Inspector displaying actual saved summary fields.

Accepts the existing setPlainText/clear calls; raw XML stays a separate,
unmodified QPlainTextEdit tab.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QScrollArea, QVBoxLayout, QWidget
from qt_property_icons import property_icon
from qt_unit_icons import UnitIcons


def inspector_fields(source):
    fields, notes = [], []
    for line in str(source or '').splitlines():
        line = line.strip()
        if not line:
            continue
        if ':' in line:
            name, value = line.split(':', 1)
            if name.strip() and value.strip():
                fields.append((name.strip(), value.strip()))
                continue
        notes.append(line)
    return fields, notes


class InspectorDetails(QWidget):
    """Drop-in read-only replacement for the Inspector Details text field."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._text = ''
        self._units = UnitIcons()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(self.scroll)
        self.content = QWidget()
        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(8, 10, 8, 10)
        self.layout.setSpacing(10)
        self.scroll.setWidget(self.content)
        self._render()

    def setPlainText(self, text):
        self._text = str(text)
        self._render()

    def clear(self):
        self.setPlainText('')

    def toPlainText(self):
        return self._text

    def _render(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        fields, notes = inspector_fields(self._text)
        if fields:
            card = QFrame()
            card.setFrameShape(QFrame.Shape.StyledPanel)
            grid = QGridLayout(card)
            grid.setContentsMargins(8, 8, 8, 8)
            grid.setColumnStretch(2, 1)
            grid.setHorizontalSpacing(9)
            grid.setVerticalSpacing(8)
            for row, (key, value) in enumerate(fields):
                glyph = QLabel()
                glyph.setFixedSize(20, 20)
                sprite = self._units.icon(value.replace(' ', ''), 20) if key == 'Unit type' else None
                glyph.setPixmap(sprite.pixmap(20, 20) if sprite is not None and not sprite.isNull()
                                else property_icon(key, 19).pixmap(19, 19))
                glyph.setToolTip(key)
                label = QLabel(key)
                label.setStyleSheet('color: palette(mid);')
                datum = QLabel(value)
                datum.setWordWrap(True)
                datum.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                grid.addWidget(glyph, row, 0, Qt.AlignmentFlag.AlignTop)
                grid.addWidget(label, row, 1, Qt.AlignmentFlag.AlignTop)
                grid.addWidget(datum, row, 2, Qt.AlignmentFlag.AlignTop)
            self.layout.addWidget(card)
        for note in notes:
            paragraph = QLabel(note)
            paragraph.setWordWrap(True)
            paragraph.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            self.layout.addWidget(paragraph)
        self.layout.addStretch(1)
