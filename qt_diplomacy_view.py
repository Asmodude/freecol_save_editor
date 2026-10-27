from qt_stage_controls import StageChangeButton
"""Diplomacy table rendering and inspection for the Qt explorer.

This read-only mixin keeps the approved two-table (rivals / native nations)
presentation while isolating it from the main window.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QComboBox, QLabel
from qt_navigation import rows_for_scope
from qt_sortable_item import SortableItem
from qt_raw_xml import formatted_record_xml


class DiplomacyViewMixin:
    def populate_diplomacy(self, query):
        records = rows_for_scope(self.document, 'Diplomacy', self.scope)
        for category, table in self.diplomacy_grids.items():
            table.blockSignals(True)
            table.setSortingEnabled(False)
            table.clearContents()
            subset = [record for record in records if record.get('category') == category
                      and (not query or query in ' '.join((
                          record.get('nation',''),record.get('stance',''),
                          record.get('tension',''))).casefold())]
            table.setRowCount(len(subset))
            for row, record in enumerate(subset):
                for col, value in enumerate((record.get('nation'),record.get('stance'),
                                              record.get('tension'))):
                    cell = SortableItem(value, col == 2)
                    cell.setData(Qt.ItemDataRole.UserRole, record)
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    table.setItem(row,col,cell)
                    if col in (1, 2):
                        owner = record.get('owner')
                        other = record.get('other')
                        field = ('stance' if col == 1 else 'tension') + '|' + other
                        current = record.get('stance' if col == 1 else 'tension')
                        if not current or current == '(absent)':
                            continue
                        holder = QWidget(table)
                        layout = QHBoxLayout(holder)
                        layout.setContentsMargins(2, 1, 2, 1)
                        staged = self.session.is_changed((owner, field))
                        selected = self.session.staged_value((owner, field),
                                                             int(current) if col == 2 else current)
                        # Stance is symmetric even though only one direction is
                        # staged. Show the pending value from either perspective.
                        if col == 1 and not staged:
                            reverse = (other, 'stance|' + owner)
                            if self.session.is_changed(reverse):
                                selected = self.session.staged_value(reverse, current)
                                staged = True
                        if staged:
                            layout.addWidget(QLabel('was ' + current, holder))
                        if col == 1:
                            editor = QComboBox(holder)
                            editor.setObjectName('diplomacyStance')
                            for choice in ('peace', 'war', 'cease_fire', 'alliance'):
                                editor.addItem(choice.replace('_', ' ').title(), choice)
                            editor.setCurrentIndex(editor.findData(selected))
                        else:
                            editor = QLineEdit(str(selected), holder)
                            editor.setObjectName('diplomacyTension')
                        editor.setProperty('relationshipKey', (owner, field))
                        button = StageChangeButton(holder)
                        button.setObjectName('stageDiplomacyRelation')
                        button.setMinimumWidth(button.sizeHint().width())
                        button.clicked.connect(
                            lambda checked=False, oid=owner, fld=field, inp=editor:
                            self.stage_relation(oid, fld, inp.currentData()
                                                if isinstance(inp, QComboBox)
                                                else inp.text()))
                        layout.addWidget(editor, 1)
                        layout.addWidget(button)
                        cell.setData(SortableItem.SourceSortRole, value)
                        cell.setText('')  # Only the QWidget editor paints this cell.
                        table.setCellWidget(row, col, holder)
            table.setSortingEnabled(True)
            for displayed_row in range(table.rowCount()):
                table.setRowHeight(displayed_row, max(table.rowHeight(displayed_row), 40))
            table.resizeColumnsToContents()
            table.setColumnWidth(1, max(table.columnWidth(1), 265))
            table.setColumnWidth(2, max(table.columnWidth(2), 185))
            table.blockSignals(False)
        self.overview.setPlainText('Editable saved relationships. Each nation appears once per tab. '
                                   'Missing saved values remain unavailable for editing.')

    def inspect_diplomacy(self, category):
        if self.group != 'Diplomacy' or self.document is None:
            return
        table = self.diplomacy_grids[category]
        row = table.currentRow()
        if row < 0 or not table.selectedItems():
            return
        item = table.item(row,0)
        element = item.data(Qt.ItemDataRole.UserRole) if item else None
        if element is None:
            return
        self.selected_element = element
        self.inspector_label.setText(element.get('nation','Diplomacy'))
        owner_id, other_id = element.get('owner'), element.get('other')
        stance = self.session.staged_value(
            (owner_id, 'stance|' + other_id), element.get('stance'))
        if not self.session.is_changed((owner_id, 'stance|' + other_id)):
            stance = self.session.staged_value(
                (other_id, 'stance|' + owner_id), stance)
        tension = self.session.staged_value(
            (owner_id, 'tension|' + other_id), element.get('tension'))
        self.details.setPlainText(
            f"Category: {category}\nOther nation: {element.get('nation')}\n"
            f"Stance: {stance}\nTension: {tension}")
        owner = self.document.players.get(element.get('owner'))
        self.raw_xml.setPlainText(formatted_record_xml(owner) if owner is not None
                                  else 'No saved source player available.')

