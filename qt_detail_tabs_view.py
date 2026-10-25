"""Read-only detail-tab rendering and contextual inspector navigation.

Extracted unchanged from the accepted Qt Explorer during Phase 2A.
"""
from PySide6.QtCore import Qt
from qt_colony_details import colony_sections, colony_detail_nodes
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
                        icon = self.unit_icons.icon(value)
                        if not icon.isNull():
                            item.setIcon(icon)
                    if col == 0 and name == 'Goods':
                        icon = self.goods_icons.icon(value)
                        if not icon.isNull():
                            item.setIcon(icon)
                    table.setItem(row, col, item)
            table.setSortingEnabled(True)
            table.resizeColumnsToContents()
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

