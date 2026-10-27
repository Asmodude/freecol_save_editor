"""Read-only detail-tab rendering and contextual inspector navigation.

Extracted unchanged from the accepted Qt Explorer during Phase 2A.
"""
from qt_stage_controls import StageChangeButton
from qt_equipment_editor import EquipmentEditor
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox, QSpinBox
from equipment_rules import ROLES, validate_equipment
from qt_equipment_controls import WheelSafeComboBox, WheelSafeSpinBox
from qt_colony_details import colony_sections, colony_detail_nodes, goods_catalog
from qt_settlement_details import settlement_units
from qt_diplomacy import settlement_alarm_rows
from qt_national_goods import colony_goods_breakdown, transported_goods_breakdown
from qt_sortable_item import SortableItem
from qt_sorting import NUMERIC_DETAIL_COLUMNS
from qt_detail_inspector import detail_inspection
from qt_raw_xml import formatted_record_xml


class DetailTabsMixin:
    def update_detail_tabs(self, element):
        self.detail_unit_id = None
        self.jump_unit_button.setEnabled(False)
        self.jump_unit_button.hide()
        colony = element if self.group == 'Colonies' else None
        settlement = element if self.group == 'Native settlements' else None
        sections = colony_sections(colony, self.document) if colony is not None else {}
        self.detail_nodes = colony_detail_nodes(colony, self.document) if colony is not None else {}
        if settlement is not None:
            sections['Affiliated units'] = settlement_units(settlement, self.document)
            sections['Alarm'] = (('Colonial nation', 'Alarm'), settlement_alarm_rows(self.document, settlement))
        if self.group == 'National Goods' and element is not None:
            sections['By colony'] = (('Colony', 'Amount'),
                colony_goods_breakdown(self.document, element.get('owner'), element.get('id')))
            sections['In transit'] = (('Unit ID', 'Unit type', 'Location', 'Amount'),
                transported_goods_breakdown(self.document, element.get('owner'), element.get('id')))
        # Qt tabs are physically removed when irrelevant, not greyed out.
        allowed = {'Overview'}
        if colony is not None:
            allowed.update(('Buildings', 'Workers', 'Stationed units', 'Goods'))
        elif settlement is not None:
            allowed.update(('Affiliated units', 'Alarm'))
        elif self.group == 'National Goods' and element is not None:
            allowed.update(('By colony', 'In transit'))
        active_name = self.tabs.tabText(self.tabs.currentIndex()) if self.tabs.currentIndex() >= 0 else 'Overview'
        for i in range(self.tabs.count()-1, -1, -1):
            self.tabs.removeTab(i)
        for name, widget in self.tab_widgets.items():
            if name in allowed:
                self.tabs.addTab(widget, name)
        if active_name in allowed:
            self.tabs.setCurrentWidget(self.tab_widgets[active_name])
        else:
            self.tabs.setCurrentWidget(self.overview)
        for name, table in self.colony_tables.items():
            table.blockSignals(True)
            table.setSortingEnabled(False)
            table.clearSelection()
            headings, records = sections.get(name, ((), ()))
            table.setRowCount(0)
            table.clearContents()
            table.setColumnCount(len(headings))
            table.setHorizontalHeaderLabels(headings)
            table.setRowCount(len(records))
            for row, values in enumerate(records):
                for col, value in enumerate(values):
                    item = SortableItem(value, headings[col] in NUMERIC_DETAIL_COLUMNS)
                    item.setData(Qt.ItemDataRole.UserRole, row)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    if col == 1 and name in ('Workers', 'Stationed units', 'Affiliated units', 'In transit'):
                        unit = self.document.unit_by_id(values[0]) if name in ('Workers', 'Stationed units') else None
                        role = (self.session.staged_value((unit.get('id'), 'equipment'),
                                (unit.get('role', 'model.role.default'), 0))[0]
                                if unit is not None else None)
                        # The table cell is a human-readable label. Manifest keys require
                        # the authoritative model.unit.* identifier instead.
                        unit_type = unit.get('unitType') if unit is not None else value
                        icon = self.unit_icons.effective_icon(unit_type, role)
                        if not icon.isNull():
                            item.setIcon(icon)
                    if col == 0 and name == 'Goods':
                        icon = self.goods_icons.icon(value)
                        if not icon.isNull():
                            item.setIcon(icon)
                    table.setItem(row, col, item)
                    if name == 'Goods' and col == 1 and colony is not None:
                        # Stable type IDs are taken from the catalog, never from
                        # readable labels or post-sort table coordinates.
                        goods_type, source = goods_catalog(colony, self.document)[row]
                        original = int(source.get('amount')) if source is not None else 0
                        edit_key = (colony.get('id'), goods_type)
                        staged = self.session.is_changed(edit_key)
                        holder = QWidget(table)
                        line = QHBoxLayout(holder)
                        line.setContentsMargins(2, 1, 2, 1)
                        if staged:
                            line.addWidget(QLabel('was ' + str(original), holder))
                        edit = QLineEdit(str(self.session.staged_value(edit_key, original)), holder)
                        edit.setObjectName('colonyGoodsAmountInput')
                        edit.setProperty('goodsTypeId', goods_type)
                        edit.setToolTip('Original stock: ' + str(original) + '; Enter to stage')
                        edit.setStyleSheet('QLineEdit { border: 2px solid ' +
                                           ('#26815A' if staged else '#76A9E8') +
                                           '; border-radius: 3px; padding: 2px; background: ' +
                                           ('#E5F5E9' if staged else '#EDF5FF') +
                                           '; color: #172B45; }')
                        button = StageChangeButton(holder)
                        button.setObjectName('stageColonyGoods')
                        button.setMinimumWidth(button.sizeHint().width())
                        button.setToolTip('Stage this goods amount')
                        valid_store = colony.find('./goodsContainer/storedGoods') is not None
                        edit.setEnabled(valid_store)
                        button.setEnabled(valid_store)
                        if not valid_store:
                            edit.setToolTip('Colony has no storedGoods element; editing unavailable')
                        edit.returnPressed.connect(
                            lambda cid=colony.get('id'), kind=goods_type, field=edit:
                            self.stage_colony_goods(cid, kind, field.text()))
                        button.clicked.connect(
                            lambda checked=False, cid=colony.get('id'), kind=goods_type, field=edit:
                            self.stage_colony_goods(cid, kind, field.text()))
                        line.addWidget(edit, 1)
                        line.addWidget(button)
                        table.setCellWidget(row, col, holder)
                    if name == 'Alarm' and col == 1 and settlement is not None:
                        # Match the same colonial-player source order as settlement_alarm_rows;
                        # never reverse-map a potentially duplicate display name.
                        colonial = [p for p in self.document.players.values()
                                    if p.get('playerType') == 'colonial']
                        counterpart = colonial[row] if row < len(colonial) else None
                        node = next((a for a in settlement.findall('alarm')
                                     if counterpart is not None and a.get('player') == counterpart.get('id')), None)
                        if node is not None and node.get('value', '').isascii() and node.get('value', '').isdecimal():
                            sid = settlement.get('id')
                            target = counterpart.get('id')
                            field = 'alarm|' + target
                            original = int(node.get('value'))
                            holder = QWidget(table)
                            layout = QHBoxLayout(holder)
                            layout.setContentsMargins(2, 1, 2, 1)
                            edit = QLineEdit(str(self.session.staged_value((sid, field), original)), holder)
                            edit.setObjectName('nativeSettlementAlarm')
                            edit.setProperty('relationshipKey', (sid, field))
                            edit.setToolTip('Directional alarm for ' + target)
                            button = StageChangeButton(holder)
                            button.setObjectName('stageSettlementAlarm')
                            button.setMinimumWidth(button.sizeHint().width())
                            edit.returnPressed.connect(
                                lambda sid=sid, field=field, edit=edit:
                                self.stage_relation(sid, field, edit.text()))
                            button.clicked.connect(
                                lambda checked=False, sid=sid, field=field, edit=edit:
                                self.stage_relation(sid, field, edit.text()))
                            layout.addWidget(edit, 1)
                            layout.addWidget(button)
                            table.setCellWidget(row, col, holder)
                    if name == 'Stationed units' and col == 3 and colony is not None:
                        # The displayed role is owned by this unit, not the colony.
                        # Capture its unique ID before the table is sorted.
                        uid = values[0]
                        unit = self.document.unit_by_id(uid)
                        if unit is not None and hasattr(self.document, 'root'):
                            holder = EquipmentEditor(self.document, unit, self.session,
                                                     context='stationed', parent=table)
                            holder.stage_requested.connect(self.stage_unit_equipment)
                            item.setData(SortableItem.SourceSortRole, value)
                            item.setText('')
                            table.setCellWidget(row, col, holder)
                    # The worker's Experience belongs to the unit, not the colony.
                    # Capture the authoritative unit ID before the table is sorted.
                    if name == 'Workers' and col == 4:
                        uid = values[0]
                        unit = self.document.unit_by_id(uid)
                        original = unit.get('experience') if unit is not None else None
                        if (original is not None and original.isascii() and original.isdecimal()):
                            edit_key = (uid, 'experience')
                            staged = self.session.is_changed(edit_key)
                            holder = QWidget(table)
                            line = QHBoxLayout(holder)
                            line.setContentsMargins(2, 1, 2, 1)
                            line.setSpacing(3)
                            if staged:
                                old = QLabel('was ' + original, holder)
                                old.setToolTip('Experience in the opened save')
                                line.addWidget(old)
                            edit = QLineEdit(str(self.session.staged_value(edit_key, int(original))), holder)
                            edit.setObjectName('workerExperienceInput')
                            edit.setToolTip('Edit worker experience (0–200); Enter to stage. Original: ' + original)
                            edit.setStyleSheet(
                                'QLineEdit { border: 2px solid ' +
                                ('#26815A' if staged else '#76A9E8') +
                                '; border-radius: 3px; padding: 2px; background: ' +
                                ('#E5F5E9' if staged else '#EDF5FF') +
                                '; color: #172B45; }')
                            button = StageChangeButton(holder)
                            button.setObjectName('stageWorkerExperience')
                            button.setMinimumWidth(button.sizeHint().width())
                            button.setToolTip('Stage this worker experience')
                            edit.returnPressed.connect(
                                lambda uid=uid, editor=edit: self.stage_overview_edit(uid, 'experience', editor.text()))
                            button.clicked.connect(
                                lambda checked=False, uid=uid, editor=edit:
                                self.stage_overview_edit(uid, 'experience', editor.text()))
                            line.addWidget(edit, 1)
                            line.addWidget(button)
                            table.setCellWidget(row, col, holder)
            if name in ('Workers', 'Stationed units'):
                # Match the main Units list: taller rows preserve full unit artwork.
                table.setIconSize(QSize(42, 42))
                for row in range(table.rowCount()):
                    table.setRowHeight(row, 44)
            table.setSortingEnabled(True)
            table.resizeColumnsToContents()
            if name == 'Stationed units' and table.columnCount() > 3:
                table.setColumnWidth(3, max(320, table.columnWidth(3)))
            table.blockSignals(False)

    def refresh_breakdown_action(self, _index):
        """Show drill-down only in National Goods → By colony."""
        table = self.colony_tables['By colony']
        relevant = (self.group == 'National Goods'
                    and self.tabs.currentWidget() is table
                    and self.selected_element is not None)
        self.jump_colony_button.setVisible(relevant)
        if not relevant:
            self.jump_colony_button.setEnabled(False)
            return
        # Opening this tab is not a selection. Require an explicit colony click.
        # Clicking or keyboard-selecting a row must establish its drill-down
        # target; merely switching to this tab does not choose a colony.
        if table.selectedItems():
            self.inspect_detail('By colony')
        else:
            self.breakdown_target = None
            self.jump_colony_button.setEnabled(False)

    def inspect_detail(self, section):
        table = self.colony_tables[section]
        chosen = table.selectedItems()
        row = chosen[0].row() if chosen else (-1 if section == 'By colony' else table.currentRow())
        if (self.selected_element is None or self.tabs.indexOf(table) < 0
                or row < 0 or row >= table.rowCount()):
            if section == 'By colony':
                self.breakdown_target = None
                self.jump_colony_button.setEnabled(False)
            return
        headings = [table.horizontalHeaderItem(col).text() for col in range(table.columnCount())]
        values = [(table.item(row, col).text() if table.item(row, col) else '')
                  for col in range(table.columnCount())]
        label, description = detail_inspection(section, headings, values)
        self.inspector_label.setText(label)
        unit_id = values[0] if section in ('Workers', 'Stationed units', 'Affiliated units') else None
        unit = self.document.unit_by_id(unit_id) if unit_id else None
        self.detail_unit_id = unit_id if unit is not None else None
        self.jump_unit_button.setVisible(unit is not None)
        self.jump_unit_button.setEnabled(unit is not None)
        if unit is not None:
            description += '\n\nFull unit attributes\n' + '\n'.join(
                f'{key}: {value}' for key, value in unit.attrib.items())
        self.details.setPlainText(description)
        exact_nodes = self.detail_nodes.get(section, ())
        source_item = table.item(row, 0)
        source_index = source_item.data(Qt.ItemDataRole.UserRole) if source_item else None
        exact = exact_nodes[source_index] if isinstance(source_index, int) and source_index < len(exact_nodes) else None
        if section == 'By colony':
            self.breakdown_target = (self.selected_element.get('id'), values[0])
            self.jump_colony_button.setEnabled(bool(self.breakdown_target[0] and self.breakdown_target[1]))
            self.details.setPlainText(description + '\n\nUse Open colony Goods to inspect this warehouse.')
            self.raw_xml.setPlainText('Read-only summary; visit the colony for source XML.')
            return
        if section == 'Goods' and exact is None:
            description += ('\n\nNo stored-goods XML entry exists for this type. '
                            'Zero is displayed for completeness; Phase 2 will need '
                            'to create a new entry when a positive amount is staged.')
            self.details.setPlainText(description)
            self.raw_xml.setPlainText('No stored-goods XML element exists for this zero-stock row.')
        else:
            self.raw_xml.setPlainText(formatted_record_xml(
                unit if unit is not None else exact if exact is not None else self.selected_element))

