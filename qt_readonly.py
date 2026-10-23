"""Phase 1: read-only PySide6 shell; launch independently with py qt_readonly.py.

The accepted Tkinter editor remains the only editor and map-rendering application.
No savegame mutation is possible from this Qt window.
"""
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPushButton, QSplitter, QTabWidget, QTableWidget,
    QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget, QPlainTextEdit, QGroupBox, QHeaderView, QSizePolicy
)
from save_document import SaveDocument
from edit_session import EditSession
import presentation
from qt_navigation import rows_for_scope, human_player_id
from qt_colony_details import colony_sections

GROUPS = ('Players', 'Colonies', 'Native settlements', 'Units')
HEADERS = {
    'Players': ('ID','Username','Nation','Type','Colonies','Settlements','Gold','Tax','Score','AI','Dead'),
    'Colonies': ('ID','Name','Owner','Location','Established','Liberty','Sons of Liberty','Production bonus'),
    'Native settlements': ('ID','Name','Owner','Location','Learnable skill','Wanted goods'),
    'Units': ('ID','Type','Owner','Location','Role','Experience toward','Experience','Moves left','Max moves','Hit points','State'),
}


class QtExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FreeCol Save Editor — Qt preview (READ ONLY)')
        self.resize(1450, 875)
        self.document = None
        self.session = EditSession()
        self.group = 'Players'
        self.scope = 'mine'
        self.visible_rows = []
        self.selected_element = None

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setSpacing(7)
        toolbar_widget = QWidget()
        toolbar_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        toolbar = QHBoxLayout(toolbar_widget)
        toolbar.setContentsMargins(0, 0, 0, 0)
        self.open_button = QPushButton('Open Save…')
        self.open_button.clicked.connect(self.open_save)
        self.map_button = QPushButton('Open Map Editor')
        self.map_button.setEnabled(False)
        self.map_button.setToolTip(
            'The existing Map Editor is available in the Tkinter application. '
            'The Qt map will be integrated in Phase 3.')
        self.heading = QLabel('Open a FreeCol save to begin · Qt read-only preview')
        toolbar.addWidget(self.open_button)
        toolbar.addWidget(self.map_button)
        toolbar.addWidget(self.heading, 1)
        layout.addWidget(toolbar_widget, 0)


        panes = QSplitter(Qt.Orientation.Horizontal)
        self.navigation = QTreeWidget()
        self.navigation.setHeaderLabel('Savegame')
        self.navigation.currentItemChanged.connect(self.navigate)
        panes.addWidget(self.navigation)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        self.search = QLineEdit()
        self.search.setPlaceholderText('Filter visible rows…')
        self.search.textChanged.connect(self.populate)
        center_layout.addWidget(self.search)
        self.grid = QTableWidget()
        self.grid.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.grid.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.grid.setAlternatingRowColors(True)
        self.grid.setSortingEnabled(False)
        self.grid.itemSelectionChanged.connect(self.inspect)
        center_layout.addWidget(self.grid, 3)

        self.tabs = QTabWidget()
        self.overview = QPlainTextEdit()
        self.overview.setReadOnly(True)
        self.tabs.addTab(self.overview, 'Overview')
        self.colony_tables = {}
        for name in ('Buildings', 'Units', 'Goods'):
            table = QTableWidget()
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            table.setAlternatingRowColors(True)
            self.tabs.addTab(table, name)
            self.colony_tables[name] = table
        center_layout.addWidget(self.tabs, 2)
        panes.addWidget(center)

        inspector = QWidget()
        inspector_layout = QVBoxLayout(inspector)
        inspector_layout.addWidget(QLabel('Inspector — current selection'))
        self.inspector_label = QLabel('Select an individual row to inspect its attributes.')
        self.inspector_label.setWordWrap(True)
        inspector_layout.addWidget(self.inspector_label)
        self.details = QPlainTextEdit()
        self.details.setReadOnly(True)
        inspector_layout.addWidget(self.details, 1)
        self.inspector_hint = QLabel('Read only · no values can be changed here')
        inspector_layout.addWidget(self.inspector_hint)
        panes.addWidget(inspector)
        panes.setChildrenCollapsible(False)
        panes.setSizes([240, 885, 325])
        layout.addWidget(panes, 1)

        self.statusBar().showMessage(
            'Read-only preview · Save As and the Map Editor remain in the Tkinter application')
        self.install_navigation()

    @staticmethod
    def _read_only_note(message):
        label = QLabel(message)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        return label

    def install_navigation(self):
        """Visible hierarchy without inventing unsupported Qt views."""
        self.navigation.clear()
        primary = QTreeWidgetItem(['My Nation'])
        primary.setFlags(primary.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        self.navigation.addTopLevelItem(primary)
        for label, group in (('Overview', 'Players'), ('Colonies', 'Colonies'),
                             ('Units', 'Units')):
            item = QTreeWidgetItem([label])
            item.setData(0, Qt.ItemDataRole.UserRole, (group, 'mine'))
            primary.addChild(item)
        others = QTreeWidgetItem(['Other Nations'])
        others.setFlags(others.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        self.navigation.addTopLevelItem(others)
        rivals = QTreeWidgetItem(['European rivals'])
        rivals.setData(0, Qt.ItemDataRole.UserRole, ('Players', 'rivals'))
        others.addChild(rivals)
        native_group = QTreeWidgetItem(['Native Nations'])
        native_group.setFlags(native_group.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        self.navigation.addTopLevelItem(native_group)
        natives = QTreeWidgetItem(['Native settlements'])
        natives.setData(0, Qt.ItemDataRole.UserRole, ('Native settlements', 'native'))
        native_group.addChild(natives)
        native_group.setExpanded(True)
        primary.setExpanded(True)
        others.setExpanded(True)
        self.navigation.setCurrentItem(primary.child(0))

    def open_save(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Open FreeCol save', str(Path.home()),
            'FreeCol saves (*.fsg);;ZIP archives (*.zip);;All files (*)')
        if not path:
            return
        try:
            document = SaveDocument.load(path)
        except Exception as exc:
            QMessageBox.critical(self, 'Could not open save', str(exc))
            return
        self.document = document
        self.heading.setText(f'{Path(path).name} · Turn {document.turn} · READ ONLY')
        self.populate()
        self.statusBar().showMessage(
            f'{len(document.players)} players · {len(document.colonies)} colonies · '
            f'{len(document.native_settlements)} native settlements · {len(document.units)} units'
            ' · Qt read-only; Map Editor in Tkinter')

    def navigate(self, current, previous):
        if current is None:
            return
        selection = current.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(selection, tuple) or len(selection)!=2:
            return
        group, scope = selection
        if group not in GROUPS:
            return
        self.group = group
        self.scope = scope
        self.populate()

    def populate(self):
        self.grid.setRowCount(0)
        self.grid.clearContents()
        self.visible_rows = []
        self.selected_element = None
        self.details.clear()
        self.inspector_label.setText('Select an individual row to inspect its attributes.')
        self.overview.clear()
        self.update_colony_tabs(None)
        self.grid.setColumnCount(len(HEADERS[self.group]))
        self.grid.setHorizontalHeaderLabels(HEADERS[self.group])
        doc = self.document
        if doc is None:
            return
        query = self.search.text().strip().casefold()
        rows = []
        for element in rows_for_scope(doc, self.group, self.scope):
            values = presentation.row_values(self.group, element, doc, self.session)
            if query and query not in ' '.join(str(value) for value in values).casefold():
                continue
            rows.append((element, values))
        self.visible_rows = [element for element, _ in rows]
        self.grid.setRowCount(len(rows))
        for row, (_, values) in enumerate(rows):
            for col, value in enumerate(values):
                cell = QTableWidgetItem('' if value is None else str(value))
                cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.grid.setItem(row, col, cell)
        self.grid.resizeColumnsToContents()
        context = {'mine':'My Nation', 'rivals':'European rivals', 'native':'Native Nations', 'all':'All'}[self.scope]
        note = ('Human player could not be uniquely identified; no player was guessed.\n' 
                if self.scope=='mine' and human_player_id(doc) is None else '')
        self.overview.setPlainText(
            f'{context} · {self.group}: {len(rows)} displayed\n' + note +
            'Choose a row above to see its full read-only record here.\n'
            'The inspector on the right shows only the currently selected object.')

    def update_colony_tabs(self, colony):
        sections = colony_sections(colony, self.document) if colony is not None else {}
        for name, table in self.colony_tables.items():
            headings, records = sections.get(name, ((), ()))
            table.setRowCount(0)
            table.clearContents()
            table.setColumnCount(len(headings))
            table.setHorizontalHeaderLabels(headings)
            table.setRowCount(len(records))
            for row, values in enumerate(records):
                for col, value in enumerate(values):
                    item = QTableWidgetItem('' if value is None else str(value))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    table.setItem(row, col, item)
            table.resizeColumnsToContents()
            self.tabs.setTabEnabled(self.tabs.indexOf(table), colony is not None)

    def inspect(self):
        row = self.grid.currentRow()
        if self.document is None or row < 0 or row >= len(self.visible_rows):
            return
        element = self.visible_rows[row]
        self.selected_element = element
        self.update_colony_tabs(element if self.group == 'Colonies' else None)
        label = element.get('name') or element.get('username') or element.get('id') or 'Record'
        self.inspector_label.setText(label)
        doc = self.document
        summary = [('Name', label), ('Category', self.group)]
        if self.group == 'Players':
            summary.extend([('Nation', presentation.short(element.get('nationId'))),
                            ('Gold', element.get('gold')), ('Tax', element.get('tax')),
                            ('AI controlled', element.get('ai'))])
        elif self.group == 'Colonies':
            summary.extend([('Owner', doc.owner_name(element.get('owner'))),
                            ('Location', doc.location_name(element.get('tile'))),
                            ('Sons of Liberty', element.get('sonsOfLiberty')),
                            ('Production bonus', element.get('productionBonus'))])
        elif self.group == 'Units':
            summary.extend([('Unit type', presentation.readable(element.get('unitType'))),
                            ('Owner', doc.owner_name(element.get('owner'))),
                            ('Location', doc.location_name(element.get('location'))),
                            ('Role', presentation.short(element.get('role'))),
                            ('Experience', element.get('experience')),
                            ('Moves left', element.get('movesLeft'))])
        else:
            summary.extend([('Owner', doc.owner_name(element.get('owner'))),
                            ('Location', doc.location_name(element.get('tile'))),
                            ('Learnable skill', presentation.short(element.get('learnableSkill')))])
        self.details.setPlainText('\n'.join(
            f'{key}: {value}' for key, value in summary if value is not None))
        self.overview.setPlainText(
            f'{label}\n\n'
            f'Category: {self.group}\n'
            f'Owner: {self.document.owner_name(element.get("owner"))}\n'
            f'Location: {self.document.location_name(element.get("tile") or element.get("location"))}\n\n'
            'Select other records in the table to inspect them. '
            'Additional object-specific detail tabs are planned for Phase 1.')


def main():
    app = QApplication(sys.argv)
    window = QtExplorer()
    window.show()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
