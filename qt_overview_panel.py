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
from qt_property_icons import property_icon
from qt_goods_icons import GoodsIcons, goods_key
from qt_flag_icons import flag_pixmap
from qt_overview_sections import overview_sections


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
        self.goods_icons = GoodsIcons()
        self._section_cards = []
        self._section_columns = 0
        self._sections_grid = None
        self._text = ''
        self._record = None
        self._document = None
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

    def set_record(self, group, record, document=None):
        self._group = group
        self._record = record
        self._document = document
        self._render()

    @staticmethod
    def _dispose(layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()
            elif item.layout() is not None:
                OverviewPanel._dispose(item.layout())

    def _empty_layout(self):
        self._dispose(self.body)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._layout_sections()

    def _layout_sections(self):
        if self._sections_grid is None or not self._section_cards:
            return
        # Respond to the *pane's* width, not the physical monitor resolution.
        width = self.scroll.viewport().width()
        columns = 3 if width >= 1180 else 2 if width >= 700 else 1
        if columns == self._section_columns:
            return
        self._section_columns = columns
        for card in self._section_cards:
            self._sections_grid.removeWidget(card)
        for index, card in enumerate(self._section_cards):
            self._sections_grid.addWidget(card, index // columns, index % columns)

    def _render(self):
        self._sections_grid = None
        self._section_cards = []
        self._section_columns = 0
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

        # Render headings with their own data, never as orphaned footnotes.
        _, sections = overview_sections(self._text)
        section_grid = QGridLayout()
        section_grid.setHorizontalSpacing(12)
        section_grid.setVerticalSpacing(12)
        self._sections_grid = section_grid
        self.body.addLayout(section_grid)
        for section_title, fields, notes in sections:
            card = QFrame()
            card.setFrameShape(QFrame.Shape.StyledPanel)
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(9, 9, 9, 9)
            card_layout.setSpacing(7)
            self._section_cards.append(card)
            if section_title != 'Colony properties' or len(sections) > 1:
                heading_label = QLabel(section_title)
                heading_font = QFont(heading_label.font())
                heading_font.setBold(True)
                heading_label.setFont(heading_font)
                card_layout.addWidget(heading_label)
            if fields:
                # Only large standalone sections need two cards; otherwise a
                # single card prevents short warehouse/building lists splitting.
                partitions = [fields]
                if section_title == 'Colony properties' and len(fields) > 7:
                    half = (len(fields) + 1) // 2
                    partitions = [fields[:half], fields[half:]]
                grids = QHBoxLayout()
                grids.setSpacing(12)
                for subset in partitions:
                    border = QFrame()
                    border.setFrameShape(QFrame.Shape.StyledPanel)
                    grid = QGridLayout(border)
                    grid.setContentsMargins(8, 8, 8, 8)
                    grid.setHorizontalSpacing(12)
                    grid.setVerticalSpacing(7)
                    grid.setColumnStretch(2, 1)
                    for row, (key, val) in enumerate(subset):
                        label = QLabel(key)
                        label.setStyleSheet('color: palette(mid);')
                        value = QLabel(val)
                        value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                        value.setWordWrap(True)
                        icon_label = QLabel()
                        icon_label.setFixedSize(26, 19)
                        owner = (self._document.players.get(self._record.get('owner'))
                                 if key == 'Owner' and self._document is not None
                                 and self._record is not None else None)
                        nation = (owner.get('nationId') or owner.get('nation')) if owner is not None else None
                        owner_flag = flag_pixmap(nation, 15) if nation else QPixmap()
                        good = self.goods_icons.icon(key, 23) if goods_key(key) else None
                        icon_label.setPixmap(owner_flag if not owner_flag.isNull() else
                                             good.pixmap(19, 19) if good is not None and not good.isNull()
                                             else property_icon(key).pixmap(19, 19))
                        icon_label.setToolTip(key)
                        grid.addWidget(icon_label, row, 0, Qt.AlignmentFlag.AlignTop)
                        grid.addWidget(label, row, 1, Qt.AlignmentFlag.AlignTop)
                        grid.addWidget(value, row, 2, Qt.AlignmentFlag.AlignTop)
                    grids.addWidget(border, 1)
                card_layout.addLayout(grids)
            for note in notes:
                note_label = QLabel(note)
                note_label.setWordWrap(True)
                note_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                card_layout.addWidget(note_label)
        self._layout_sections()
        self.body.addStretch(1)
