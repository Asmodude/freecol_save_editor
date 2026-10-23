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
    QWidget, QPlainTextEdit, QGroupBox, QHeaderView
)
from save_document import SaveDocument
from edit_session import EditSession
import presentation

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
        self.visible_rows = []
        self.selected_element = None

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        toolbar = QHBoxLayout()
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
        layout.addLayout(toolbar)

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
        self.tabs.addTab(self._read_only_note(
            'Detailed Buildings, Units, Goods and Production workspaces '
            'will be introduced as Phase 1 progresses.'), 'Details (planned)')
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
        layout.addWidget(panes)

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
        self.navigation.clear()
        for group in GROUPS:
            item = QTreeWidgetItem([group])
            item.setData(0, Qt.ItemDataRole.UserRole, group)
            self.navigation.addTopLevelItem(item)
        self.navigation.setCurrentItem(self.navigation.topLevelItem(0))

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
        self.group = current.data(0, Qt.ItemDataRole.UserRole) or 'Players'
        self.populate()

    def populate(self):
        self.grid.setRowCount(0)
        self.grid.clearContents()
        self.visible_rows = []
        self.selected_element = None
        self.details.clear()
        self.inspector_label.setText('Select an individual row to inspect its attributes.')
        self.overview.clear()
        self.grid.setColumnCount(len(HEADERS[self.group]))
        self.grid.setHorizontalHeaderLabels(HEADERS[self.group])
        doc = self.document
        if doc is None:
            return
        query = self.search.text().strip().casefold()
        rows = []
        for element in doc.records.get(self.group, ()):
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
        self.overview.setPlainText(
            f'{self.group}: {len(rows)} displayed\n'
            'Choose a row above to see its full read-only record here.\n'
            'The inspector on the right shows only the currently selected object.')

    def inspect(self):
        row = self.grid.currentRow()
        if self.document is None or row < 0 or row >= len(self.visible_rows):
            return
        element = self.visible_rows[row]
        self.selected_element = element
        label = element.get('name') or element.get('username') or element.get('id') or 'Record'
        self.inspector_label.setText(label)
        self.details.setPlainText('\n'.join(f'{key}: {value}' for key, value in element.attrib.items()))
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
