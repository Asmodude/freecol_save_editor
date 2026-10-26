"""Graphical, strictly read-only Overview compatible with existing summary callers.

The source summary remains authoritative; this widget changes presentation only.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QScrollArea, QLineEdit, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget, QComboBox, QSpinBox,
)
from colony_graphics import resolve_colony_graphic
from qt_property_icons import property_icon
from qt_goods_icons import GoodsIcons, goods_key
from qt_flag_icons import flag_pixmap
from qt_unit_icons import UnitIcons
from qt_overview_sections import overview_sections
from equipment_rules import ROLES, validate_equipment


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
    """Overview with scoped inline editing of supported fields."""
    edit_requested = Signal(str, str, str)
    equipment_requested = Signal(str, str, int)
    skill_requested = Signal(str, str)
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
        self.unit_icons = UnitIcons()
        self._section_cards = []
        self._section_columns = 0
        self._sections_grid = None
        self._text = ''
        self._record = None
        self._document = None
        self._group = None
        self._session = None
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

    def set_record(self, group, record, document=None, session=None):
        self._group = group
        self._record = record
        self._document = document
        self._session = session
        self._render()

    @staticmethod
    def _dispose(layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget() is not None:
                # Detach immediately so findChild and signal lookups cannot
                # discover an obsolete editor while Qt defers deletion.
                widget = item.widget()
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()
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
                        numeric_fields = ({'Gold': 'gold', 'Tax': 'tax'} if self._group == 'Players' else
                                          {'Experience': 'experience', 'Moves left': 'movesLeft'} if self._group == 'Units' else
                                          {'Sons of Liberty': 'sonsOfLibertyTarget'} if self._group == 'Colonies' else {})
                        numeric_field = numeric_fields.get(key)
                        source_field = 'sonsOfLiberty' if numeric_field == 'sonsOfLibertyTarget' else numeric_field
                        eligible_colony_sol = True
                        if numeric_field == 'sonsOfLibertyTarget':
                            members = sum(1 for member in self._record.iter('unit') if member.get('id')) if self._record is not None else 0
                            try:
                                expected = min(100, int(self._record.get('liberty')) * 100 // (members * 200))
                                eligible_colony_sol = int(self._record.get('sonsOfLiberty')) == expected
                            except (ValueError, TypeError, ZeroDivisionError):
                                eligible_colony_sol = False
                        editable_numeric = (numeric_field is not None
                                         and self._record is not None and self._session is not None
                                         and (numeric_field != 'gold' or self._record.get('gold') != '-2147483648')
                                         and (numeric_field != 'tax' or not (self._record.get('playerType', '').lower() in ('native', 'indian') or self._record.get('gold') == '-2147483648'))
                                         and eligible_colony_sol
                                         and (self._record.get(source_field) or '').isascii()
                                         and (self._record.get(source_field) or '').isdecimal())
                        if (self._group == 'Native settlements' and key == 'Learnable skill'
                                and self._record is not None and self._session is not None
                                and self._document is not None):
                            sid = self._record.get('id')
                            current = self._record.get('learnableSkill')
                            choices = list(getattr(self._document, 'professions', ()) or ())
                            value = QWidget()
                            layout = QHBoxLayout(value)
                            layout.setContentsMargins(0, 0, 0, 0)
                            selector = QComboBox(value)
                            selector.setObjectName('nativeLearnableSkill')
                            for skill in choices:
                                selector.addItem(skill.rsplit('.', 1)[-1].replace('_', ' ').title(), skill)
                            proposed = self._session.staged_value((sid, 'learnableSkill'), current)
                            index = selector.findData(proposed)
                            if index >= 0:
                                selector.setCurrentIndex(index)
                            button = QPushButton('✎', value)
                            button.setObjectName('stageNativeLearnableSkill')
                            button.setEnabled(index >= 0)
                            button.setToolTip('Stage a skill actually taught in the opened save')
                            button.clicked.connect(
                                lambda checked=False, sid=sid, selector=selector:
                                self.skill_requested.emit(sid, selector.currentData()))
                            layout.addWidget(selector, 1)
                            layout.addWidget(button)
                        elif (self._group == 'Units' and key == 'Role' and self._record is not None
                                and self._document is not None and self._session is not None):
                            uid = self._record.get('id')
                            original_role = self._record.get('role', 'model.role.default')
                            original_count = int(self._record.get('roleCount', '1'))
                            staged_role, staged_count = self._session.staged_value(
                                (uid, 'equipment'), (original_role, original_count))
                            value = QWidget()
                            edit_layout = QHBoxLayout(value)
                            edit_layout.setContentsMargins(0, 0, 0, 0)
                            selector = QComboBox(value)
                            selector.setObjectName('unitEquipmentRole')
                            for candidate in ROLES:
                                # Validate against the opened-save unit and ruleset.
                                try:
                                    validate_equipment(self._document.root, self._record, candidate, 1)
                                except (ValueError, TypeError):
                                    continue
                                selector.addItem(candidate.rsplit('.', 1)[-1].replace('_', ' ').title(), candidate)
                            count = QSpinBox(value)
                            count.setObjectName('unitEquipmentCount')
                            def sync_count(index, selector=selector, count=count, doc=self._document):
                                role_id = selector.itemData(index)
                                roles = [r for r in doc.root.iter('role') if r.get('id') == role_id]
                                limit = int(roles[0].get('maximum-count', '1')) if len(roles) == 1 else 1
                                count.setRange(1, max(1, limit))
                                count.setEnabled(limit > 1)
                                count.setToolTip('Pioneer: 1–5 means 20–100 tools' if role_id == 'model.role.pioneer'
                                                 else 'Equipment count defined by the save ruleset')
                            selector.currentIndexChanged.connect(sync_count)
                            tools_label = QLabel('', value)
                            tools_label.setObjectName('pioneerToolQuantity')
                            def sync_tools(*_args, selector=selector, count=count, label=tools_label):
                                label.setText(f'{count.value() * 20} tools' if selector.currentData() == 'model.role.pioneer' else '')
                            selector.currentIndexChanged.connect(sync_tools)
                            count.valueChanged.connect(sync_tools)
                            chosen = selector.findData(staged_role)
                            # Hardy Pioneer default equipment naturally suggests Pioneer.
                            if (not self._session.is_changed((uid, 'equipment'))
                                    and original_role == 'model.role.default'
                                    and 'hardypioneer' in (self._record.get('unitType') or '').lower()):
                                pioneer = selector.findData('model.role.pioneer')
                                if pioneer >= 0:
                                    chosen = pioneer
                            if chosen >= 0:
                                selector.setCurrentIndex(chosen)
                                sync_count(chosen)
                                count.setValue(staged_count if staged_role == selector.currentData() else 1)
                            else:
                                selector.setEnabled(False)
                                count.setEnabled(False)
                                selector.setToolTip('No eligible roles can be verified from the saved ruleset')
                            button = QPushButton('✎', value)
                            button.setObjectName('stageUnitEquipment')
                            button.setToolTip('Stage role and equipment count together')
                            button.setEnabled(chosen >= 0)
                            button.clicked.connect(
                                lambda checked=False, rid=uid, choose=selector, qty=count:
                                self.equipment_requested.emit(rid, choose.currentData(), qty.value()))
                            edit_layout.addWidget(selector, 2)
                            sync_tools()
                            edit_layout.addWidget(count, 1)
                            edit_layout.addWidget(tools_label)
                            edit_layout.addWidget(button)
                        elif editable_numeric:
                            record_id = self._record.get('id')
                            original = self._record.get(source_field)
                            value = QWidget()
                            edit_layout = QHBoxLayout(value)
                            edit_layout.setContentsMargins(0, 0, 0, 0)
                            field = QLineEdit(str(self._session.staged_value((record_id, numeric_field), int(original))))
                            field.setObjectName('inline' + numeric_field.title() + 'Input')
                            staged = self._session.is_changed((record_id, numeric_field))
                            field.setToolTip(f'Original save: {original}. Press Enter to stage.' +
                                             (' Liberty, rebels/tories and production bonus recalculate on export.'
                                              if numeric_field == 'sonsOfLibertyTarget' else ''))
                            field.setStyleSheet('QLineEdit { border: 2px solid ' +
                                                ('#26815A' if staged else '#76A9E8') + '; '
                                                'border-radius: 3px; padding: 3px; '
                                                'background: ' + ('#E5F5E9' if staged else '#EDF5FF') +
                                                '; color: #172B45; }')
                            if staged:
                                original_label = QLabel('was ' + original)
                                original_label.setObjectName('inline' + numeric_field.title() + 'Original')
                                original_label.setToolTip('Value in opened save')
                                edit_layout.addWidget(original_label)
                            button = QPushButton('✎')
                            button.setObjectName('stageInline' + numeric_field.title())
                            button.setFixedWidth(30)
                            button.setToolTip('Stage this value')
                            field.returnPressed.connect(
                                lambda rid=record_id, field_id=numeric_field, edit=field: self.edit_requested.emit(rid, field_id, edit.text()))
                            button.clicked.connect(
                                lambda checked=False, rid=record_id, field_id=numeric_field, edit=field: self.edit_requested.emit(rid, field_id, edit.text()))
                            edit_layout.addWidget(field, 1)
                            edit_layout.addWidget(button)
                        else:
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
                        unit_image = (self.unit_icons.icon(self._record.get('unitType'), 19)
                                      if key == 'Type' and self._group == 'Units'
                                      and self._record is not None else None)
                        icon_label.setPixmap(unit_image.pixmap(19, 19) if unit_image is not None and not unit_image.isNull() else
                                             owner_flag if not owner_flag.isNull() else
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
