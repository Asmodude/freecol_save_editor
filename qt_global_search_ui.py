"""Global-search dialog and navigation behaviour, extracted from QtExplorer."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QTableWidget, QLabel

from qt_sortable_item import SortableItem
from qt_global_search import global_results
from qt_navigation import human_player_id
from qt_navigation_lookup import find_navigation_item


class GlobalSearchMixin:
    def open_global_search(self):
        if self.document is None:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle('Search all saved records')
        dialog.resize(760, 490)
        layout = QVBoxLayout(dialog)
        field = QLineEdit()
        field.setPlaceholderText('Search players, colonies, settlements and units…')
        results = QTableWidget()
        results.setColumnCount(4)
        results.setHorizontalHeaderLabels(('Category','Name','Owner','ID'))
        results.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        results.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        results.setAlternatingRowColors(True)
        results.setSortingEnabled(True)
        status = QLabel('Enter a name, profession or record ID.')
        layout.addWidget(field)
        layout.addWidget(results, 1)
        layout.addWidget(status)
        matches = []

        def update():
            nonlocal matches
            matches = global_results(self.document, field.text())
            results.setSortingEnabled(False)
            results.setRowCount(len(matches))
            for row, (group, element, name, owner) in enumerate(matches):
                for col, value in enumerate((group, name, owner, element.get('id',''))):
                    cell = SortableItem(value)
                    cell.setData(Qt.ItemDataRole.UserRole, row)
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    results.setItem(row, col, cell)
            results.setSortingEnabled(True)
            status.setText(f'{len(matches)} matches (first 250 shown). Double-click to open.'
                           if field.text().strip() else 'Enter a name, profession or record ID.')

        def open_match(row, _column):
            cell = results.item(row, 0)
            source_index = cell.data(Qt.ItemDataRole.UserRole) if cell is not None else None
            if isinstance(source_index, int) and 0 <= source_index < len(matches):
                group, element, _name, _owner = matches[source_index]
                dialog.accept()
                self.navigate_to_global_result(group, element)

        field.textChanged.connect(update)
        results.cellDoubleClicked.connect(open_match)
        field.setFocus()
        dialog.exec()

    def navigate_to_global_result(self, group, element):
        """Use an existing navigation scope; never fabricate a savegame record."""
        record_id = element.get('id')
        owner = element.get('owner')
        own = human_player_id(self.document)
        if group == 'Colonies':
            scope = 'colony-id:' + record_id
        elif group == 'Native settlements':
            scope = 'settlement-id:' + record_id
        elif group == 'Players':
            scope = 'mine' if record_id == own else 'player:' + record_id
        else:
            scope = 'mine' if owner == own else 'player:' + owner
        target = find_navigation_item(self.navigation, group, scope)
        if target is None:
            return
        self.search.blockSignals(True)
        self.search.clear()
        self.search.blockSignals(False)
        if self.navigation.currentItem() is target:
            self.populate()
        else:
            self.navigation.setCurrentItem(target)
        if group == 'Founding Fathers':
            if element.get('status') == 'Recruiting':
                self.inspect_recruiting_father()
                return
            for row in range(self.grid.rowCount()):
                cell=self.grid.item(row,0)
                if cell is not None and cell.text() == element.get('name'):
                    self.grid.selectRow(row)
                    self.grid.scrollToItem(cell)
                    return
            # Offered fathers are not Congress members; inspect the virtual record.
            self.inspect_father_record(element)
            return
        for row in range(self.grid.rowCount()):
            cell = self.grid.item(row, 0)
            if cell is None:
                continue
            index = cell.data(Qt.ItemDataRole.UserRole)
            if isinstance(index, int) and index < len(self.visible_rows):
                if self.visible_rows[index] is element:
                    self.grid.selectRow(row)
                    self.grid.scrollToItem(cell)
                    return

