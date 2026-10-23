"""Phase 1 experimental read-only Qt shell.

Launch separately: py qt_readonly.py
The accepted Tk editor and all save-editing paths are untouched.
"""
import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication,QFileDialog,QHBoxLayout,QLabel,QLineEdit,
    QMainWindow,QMessageBox,QPushButton,QSplitter,QTabWidget,QTableWidget,
    QTableWidgetItem,QTreeWidget,QTreeWidgetItem,QVBoxLayout,QWidget,QPlainTextEdit)
from save_document import SaveDocument
from edit_session import EditSession
import presentation

GROUPS=('Players','Colonies','Native settlements','Units')


class QtExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FreeCol Save Editor — Qt preview (READ ONLY)')
        self.resize(1300,800)
        self.document=None
        self.session=EditSession()
        root=QWidget()
        self.setCentralWidget(root)
        layout=QVBoxLayout(root)
        bar=QHBoxLayout()
        self.heading=QLabel('Open a FreeCol save to begin · read-only Qt preview')
        self.open_button=QPushButton('Open .fsg…')
        self.open_button.clicked.connect(self.open_save)
        bar.addWidget(self.heading,1)
        bar.addWidget(self.open_button)
        layout.addLayout(bar)
        panes=QSplitter(Qt.Orientation.Horizontal)
        self.navigation=QTreeWidget()
        self.navigation.setHeaderLabel('Navigation')
        self.navigation.currentItemChanged.connect(self.navigate)
        panes.addWidget(self.navigation)
        center=QWidget()
        center_layout=QVBoxLayout(center)
        self.search=QLineEdit()
        self.search.setPlaceholderText('Filter visible rows…')
        self.search.textChanged.connect(self.populate)
        center_layout.addWidget(self.search)
        self.tabs=QTabWidget()
        self.grid=QTableWidget()
        self.grid.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.grid.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.grid.itemSelectionChanged.connect(self.inspect)
        self.tabs.addTab(self.grid,'Overview')
        center_layout.addWidget(self.tabs)
        panes.addWidget(center)
        self.details=QPlainTextEdit()
        self.details.setReadOnly(True)
        panes.addWidget(self.details)
        panes.setSizes([240,800,260])
        layout.addWidget(panes)
        self.group='Players'
        self.statusBar().showMessage('Read only — Save As remains available exclusively in the Tk editor')
        self.install_navigation()

    def install_navigation(self):
        self.navigation.clear()
        for group in GROUPS:
            item=QTreeWidgetItem([group])
            item.setData(0,Qt.ItemDataRole.UserRole,group)
            self.navigation.addTopLevelItem(item)
        self.navigation.setCurrentItem(self.navigation.topLevelItem(0))

    def open_save(self):
        path,_=QFileDialog.getOpenFileName(self,'Open FreeCol save',str(Path.home()),
                                           'FreeCol saves (*.fsg);;ZIP archives (*.zip);;All files (*)')
        if not path:
            return
        try:
            document=SaveDocument.load(path)
        except Exception as exc:
            QMessageBox.critical(self,'Could not open save',str(exc))
            return
        self.document=document
        self.heading.setText(f'{Path(path).name} · Turn {document.turn} · READ ONLY')
        self.details.clear()
        self.populate()
        self.statusBar().showMessage(
            f'{len(document.players)} players · {len(document.colonies)} colonies · '
            f'{len(document.native_settlements)} native settlements · {len(document.units)} units')

    def navigate(self,current,previous):
        if current is None:
            return
        self.group=current.data(0,Qt.ItemDataRole.UserRole) or 'Players'
        self.populate()

    def populate(self):
        self.grid.clear()
        doc=self.document
        if doc is None:
            self.grid.setRowCount(0)
            self.grid.setColumnCount(0)
            return
        rows=[]
        query=self.search.text().strip().casefold()
        for element in doc.records.get(self.group,()):
            values=presentation.row_values(self.group,element,doc,self.session)
            if query and query not in ' '.join(str(value) for value in values).casefold():
                continue
            rows.append((element,values))
        self.visible_rows=[element for element,values in rows]
        cols=max((len(values) for element,values in rows),default={
            'Players':11,'Colonies':8,'Native settlements':6,'Units':11}[self.group])
        self.grid.setColumnCount(cols)
        self.grid.setRowCount(len(rows))
        self.grid.setHorizontalHeaderLabels([f'Field {i+1}' for i in range(cols)])
        for row,(element,values) in enumerate(rows):
            for col,value in enumerate(values):
                cell=QTableWidgetItem('' if value is None else str(value))
                cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.grid.setItem(row,col,cell)
        self.grid.resizeColumnsToContents()

    def inspect(self):
        if self.document is None:
            return
        row=self.grid.currentRow()
        if row<0 or row>=len(getattr(self,'visible_rows',())):
            return
        element=self.visible_rows[row]
        self.details.setPlainText('\n'.join(f'{key}: {value}' for key,value in element.attrib.items()))


def main():
    app=QApplication(sys.argv)
    window=QtExplorer()
    window.show()
    return app.exec()


if __name__=='__main__':
    raise SystemExit(main())
