"""Diplomacy table rendering and inspection for the Qt explorer.

This read-only mixin keeps the approved two-table (rivals / native nations)
presentation while isolating it from the main window.
"""
from PySide6.QtCore import Qt
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
            table.setSortingEnabled(True)
            table.resizeColumnsToContents()
            table.blockSignals(False)
        self.overview.setPlainText('Read-only relationships. Each nation appears once per tab. '
                                   'Missing saved values are marked (absent).')

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
        self.details.setPlainText(
            f"Category: {category}\nOther nation: {element.get('nation')}\n"
            f"Stance: {element.get('stance')}\nTension: {element.get('tension')}")
        owner = self.document.players.get(element.get('owner'))
        self.raw_xml.setPlainText(formatted_record_xml(owner) if owner is not None
                                  else 'No saved source player available.')

