"""Graphical, strictly read-only Overview compatible with existing summary callers.

The source summary remains authoritative; this widget changes presentation only.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QScrollArea,
    QSizePolicy, QVBoxLayout, QWidget,
)
from colony_graphics import resolve_colony_graphic


def summary_parts(text):
    """Separate existing summary prose from saved/derived label-value rows."""
    heading = ''
    fields = []
    notes = []
    for line in text.splitlines():
        value = line.strip()
        if not value:
            continue
        if not heading:
            heading = value
        elif ':' in value and not value.startswith('Select '):
            key, val = value.split(':', 1)
            if key.strip() and val.strip():
                fields.append((key.strip(), val.strip()))
            else:
                notes.append(value)
        else:
            notes.append(value)
    return heading, fields, notes


class OverviewPanel(QWidget):
    """Drop-in replacement for the old plain-text Overview summaries."""
    def __init__(self, parent=None):
        super().__init__(parent)
        frame = QVBoxLayout(self)
        frame.setContentsMargins(0, 0, 0, 0)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        frame.addWidget(self.scroll)
        self.content = QWidget()
        self.body = QVBoxLayout(self.content)
        self.body.setContentsMargins(12, 12, 12, 12)
        self.body.setSpacing(10)
        self.scroll.setWidget(self.content)
        self._text = ''
        self._record = None
        self._group = None
        self._render()

    def setPlainText(self, text):
        self._text = str(text)
        self._render()

    def toPlainText(self):
        return self._text

    def clear(self):
        self._text = ''
        self._record = None
        self._group = None
        self._render()

    def set_record(self, group, record):
        self._group = group
        self._record = record
        self._render()

    def _empty_layout(self):
        while self.body.count():
            item = self.body.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _render(self):
        self._empty_layout()
        title, fields, notes = summary_parts(self._text)
        header = QHBoxLayout()
        header.setSpacing(15)
        if self._group == 'Colonies' and self._record is not None:
            art = resolve_colony_graphic(self._record)
            if art.image_path is not None:
                pixmap = QPixmap(str(art.image_path))
                if not pixmap.isNull():
                    image = QLabel()
                    image.setPixmap(pixmap.scaled(
                        240, 170, Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation))
                    image.setAlignment(Qt.AlignmentFlag.AlignTop)
                    header.addWidget(image)
        title_box = QVBoxLayout()
        title_label = QLabel(title or 'Overview')
        title_font = QFont(title_label.font())
        title_font.setBold(True)
        title_font.setPointSize(max(12, title_font.pointSize() + 2))
        title_label.setFont(title_font)
        title_label.setWordWrap(True)
        title_box.addWidget(title_label)
        title_box.addStretch(1)
        header.addLayout(title_box, 1)
        self.body.addLayout(header)

        # Two bordered property tables, each containing two columns (label/value).
        if fields:
            midpoint = (len(fields) + 1) // 2
            grids = QHBoxLayout()
            grids.setSpacing(12)
            for subset in (fields[:midpoint], fields[midpoint:]):
                if not subset:
                    continue
                border = QFrame()
                border.setFrameShape(QFrame.Shape.StyledPanel)
                grid = QGridLayout(border)
                grid.setContentsMargins(8, 8, 8, 8)
                grid.setHorizontalSpacing(12)
                grid.setVerticalSpacing(7)
                grid.setColumnStretch(1, 1)
                for row, (key, val) in enumerate(subset):
                    label = QLabel(key)
                    label.setStyleSheet('color: palette(mid);')
                    value = QLabel(val)
                    value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                    value.setWordWrap(True)
                    grid.addWidget(label, row, 0, Qt.AlignmentFlag.AlignTop)
                    grid.addWidget(value, row, 1, Qt.AlignmentFlag.AlignTop)
                grids.addWidget(border, 1)
            self.body.addLayout(grids)
        for note in notes:
            note_label = QLabel(note)
            note_label.setWordWrap(True)
            note_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            self.body.addWidget(note_label)
        self.body.addStretch(1)
