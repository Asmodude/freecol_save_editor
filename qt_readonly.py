"""Phase 1: read-only PySide6 shell; launch independently with py qt_readonly.py.

The accepted Tkinter editor remains the only editor and map-rendering application.
No savegame mutation is possible from this Qt window.
"""
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QBrush
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPushButton, QSplitter, QTabWidget, QTableWidget,
    QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget, QPlainTextEdit, QGroupBox, QHeaderView, QSizePolicy, QStyle
)
from save_document import SaveDocument
from edit_session import EditSession
import presentation
from qt_navigation import rows_for_scope, human_player_id
from qt_colony_details import colony_sections, colony_detail_nodes
from qt_settlement_details import settlement_units
from qt_overview import record_overview
from qt_detail_inspector import detail_inspection
from qt_raw_xml import formatted_record_xml

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
        self.detail_unit_id = None
        self.detail_nodes = {}

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
        self.navigation.setHeaderLabel('SAVEGAME EXPLORER')
        self.navigation.setIndentation(19)
        self.navigation.setUniformRowHeights(True)
        self.navigation.setAnimated(True)
        self.navigation.setAlternatingRowColors(True)
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
        for name in ('Buildings', 'Workers', 'Stationed units', 'Goods', 'Affiliated units'):
            table = QTableWidget()
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            table.setAlternatingRowColors(True)
            table.itemSelectionChanged.connect(lambda section=name: self.inspect_detail(section))
            self.tabs.addTab(table, name)
            self.colony_tables[name] = table
        self.tab_widgets = {'Overview': self.overview, **self.colony_tables}
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
        self.inspector_tabs = QTabWidget()
        self.inspector_tabs.addTab(self.details, 'Details')
        self.raw_xml = QPlainTextEdit()
        self.raw_xml.setReadOnly(True)
        self.inspector_tabs.addTab(self.raw_xml, 'Raw XML')
        inspector_layout.addWidget(self.inspector_tabs, 1)
        self.jump_unit_button = QPushButton('Open full unit record →')
        self.jump_unit_button.setEnabled(False)
        self.jump_unit_button.clicked.connect(self.open_detail_unit)
        inspector_layout.addWidget(self.jump_unit_button)
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
        """Build the approved navigation structure; disable views not implemented yet."""
        self.navigation.blockSignals(True)
        self.navigation.clear()

        def entry(parent, label, group=None, scope=None, ready=True, kind='section'):
            item = QTreeWidgetItem([label])
            icons = {
                'nation': QStyle.StandardPixmap.SP_ComputerIcon,
                'section': QStyle.StandardPixmap.SP_DirIcon,
                'colony': QStyle.StandardPixmap.SP_FileIcon,
                'planned': QStyle.StandardPixmap.SP_FileDialogDetailedView,
            }
            item.setIcon(0, self.style().standardIcon(icons['planned' if not ready else kind]))
            if kind == 'nation':
                font = QFont(item.font(0))
                font.setBold(True)
                item.setFont(0, font)
            if parent is None:
                self.navigation.addTopLevelItem(item)
            else:
                parent.addChild(item)
            if group and ready:
                item.setData(0, Qt.ItemDataRole.UserRole, (group, scope))
            else:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                if not ready:
                    item.setText(0, label + '  (planned)')
                    item.setForeground(0, QBrush(self.palette().color(self.foregroundRole()).lighter(135)))
                    item.setToolTip(0, 'Not yet implemented in the Phase 1 Qt preview')
            return item

        doc = self.document
        own = human_player_id(doc) if doc else None
        human = doc.players.get(own) if doc and own else None
        nation = presentation.readable(human.get('nationId')) if human is not None else 'My Nation'
        my = entry(None, nation + ' (Player)', kind='nation')
        overview = entry(my, 'Overview', 'Players', 'mine')
        entry(my, 'Diplomacy', ready=False)
        my_colonies = entry(my, 'Colonies', 'Colonies', 'mine')
        if doc and own:
            for colony in sorted((c for c in doc.colonies if c.get('owner') == own),
                                 key=lambda c: (c.get('name') or '').casefold()):
                entry(my_colonies, colony.get('name') or colony.get('id'),
                      'Colonies', 'colony-id:' + colony.get('id'), kind='colony')
        entry(my, 'Units', 'Units', 'mine')
        for label in ('Goods', 'Research', 'Founding Fathers', 'Player Options'):
            entry(my, label, ready=False)

        rivals = entry(None, 'Rival Nations', kind='nation')
        entry(rivals, 'All European rivals', 'Players', 'rivals')
        natives = entry(None, 'Native Nations', kind='nation')
        entry(natives, 'All native settlements', 'Native settlements', 'native')
        if doc:
            for player in doc.players.values():
                pid = player.get('id')
                if pid == own:
                    continue
                nation_id = player.get('nationId') or player.get('nation')
                if player.get('playerType') == 'colonial':
                    label = presentation.readable(nation_id) or pid
                    rival = entry(rivals, label, kind='nation')
                    entry(rival, 'Overview', 'Players', 'player:' + pid)
                    entry(rival, 'Diplomacy', ready=False)
                    colony_group = entry(rival, 'Colonies', 'Colonies', 'player:' + pid)
                    for colony in sorted((c for c in doc.colonies if c.get('owner') == pid),
                                         key=lambda c: (c.get('name') or '').casefold()):
                        entry(colony_group, colony.get('name') or colony.get('id'),
                              'Colonies', 'colony-id:' + colony.get('id'))
                    entry(rival, 'Units', 'Units', 'player:' + pid)
                    for section in ('Goods', 'Research', 'Founding Fathers', 'Player Options'):
                        entry(rival, section, ready=False)
                elif player.get('playerType') in ('indian', 'native'):
                    label = presentation.readable(nation_id) or pid
                    native = entry(natives, label, kind='nation')
                    entry(native, 'Settlements', 'Native settlements', 'native-owner:' + pid)
                    entry(native, 'Units', 'Units', 'player:' + pid)

        entry(None, 'Map', ready=False)
        entry(None, 'Game Options', ready=False)
        my.setExpanded(True)
        rivals.setExpanded(True)
        natives.setExpanded(True)
        self.navigation.blockSignals(False)
        self.navigation.setCurrentItem(overview)

    @staticmethod
    def _default_save_directory():
        # DEVELOPMENT ONLY: remove this local override before release packaging.
        dev_save = Path(r'C:\Users\morte\OneDrive\Dokumenter\freecol\save')
        return dev_save if dev_save.is_dir() else Path.home()

    def open_save(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Open FreeCol save', str(self._default_save_directory()),
            'FreeCol saves (*.fsg);;ZIP archives (*.zip);;All files (*)')
        if not path:
            return
        try:
            document = SaveDocument.load(path)
        except Exception as exc:
            QMessageBox.critical(self, 'Could not open save', str(exc))
            return
        self.document = document
        self.install_navigation()
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
        if group == 'Colonies' and scope.startswith('colony-id:'):
            self.search.blockSignals(True)
            self.search.clear()
            self.search.blockSignals(False)
        self.populate()
        if group == 'Colonies' and scope.startswith('colony-id:') and self.visible_rows:
            self.grid.selectRow(0)

    def populate(self):
        self.grid.setRowCount(0)
        self.grid.clearContents()
        self.visible_rows = []
        self.selected_element = None
        self.detail_unit_id = None
        self.jump_unit_button.setEnabled(False)
        self.details.clear()
        self.raw_xml.clear()
        self.inspector_label.setText('Select an individual row to inspect its attributes.')
        self.overview.clear()
        self.update_detail_tabs(None)
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
        context = self.navigation.currentItem().text(0) if self.navigation.currentItem() else self.scope
        note = ('Human player could not be uniquely identified; no player was guessed.\n' 
                if self.scope=='mine' and human_player_id(doc) is None else '')
        self.overview.setPlainText(
            f'{context} · {self.group}: {len(rows)} displayed\n' + note +
            'Choose a row above to see its full read-only record here.\n'
            'The inspector on the right shows only the currently selected object.')

    def update_detail_tabs(self, element):
        self.detail_unit_id = None
        self.jump_unit_button.setEnabled(False)
        colony = element if self.group == 'Colonies' else None
        settlement = element if self.group == 'Native settlements' else None
        sections = colony_sections(colony, self.document) if colony is not None else {}
        self.detail_nodes = colony_detail_nodes(colony, self.document) if colony is not None else {}
        if settlement is not None:
            sections['Affiliated units'] = settlement_units(settlement, self.document)
        # Qt tabs are physically removed when irrelevant, not greyed out.
        allowed = {'Overview'}
        if colony is not None:
            allowed.update(('Buildings', 'Workers', 'Stationed units', 'Goods'))
        elif settlement is not None:
            allowed.add('Affiliated units')
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
            table.clearSelection()
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
            table.blockSignals(False)

    def inspect_detail(self, section):
        table = self.colony_tables[section]
        row = table.currentRow()
        if (self.selected_element is None or self.tabs.indexOf(table) < 0
                or row < 0 or row >= table.rowCount()):
            return
        headings = [table.horizontalHeaderItem(col).text() for col in range(table.columnCount())]
        values = [(table.item(row, col).text() if table.item(row, col) else '')
                  for col in range(table.columnCount())]
        label, description = detail_inspection(section, headings, values)
        self.inspector_label.setText(label)
        unit_id = values[0] if section in ('Workers', 'Stationed units', 'Affiliated units') else None
        unit = self.document.unit_by_id(unit_id) if unit_id else None
        self.detail_unit_id = unit_id if unit is not None else None
        self.jump_unit_button.setEnabled(unit is not None)
        if unit is not None:
            description += '\n\nFull unit attributes\n' + '\n'.join(
                f'{key}: {value}' for key, value in unit.attrib.items())
        self.details.setPlainText(description)
        exact_nodes = self.detail_nodes.get(section, ())
        exact = exact_nodes[row] if row < len(exact_nodes) else None
        self.raw_xml.setPlainText(formatted_record_xml(unit if unit is not None else exact if exact is not None else self.selected_element))

    def open_detail_unit(self):
        unit_id = self.detail_unit_id
        if not unit_id or not self.document:
            return
        unit = self.document.unit_by_id(unit_id)
        if unit is None:
            return
        owner = unit.get('owner')
        scope = 'mine' if owner == human_player_id(self.document) else 'player:' + owner if owner else 'all'
        def matching_item(parent):
            for i in range(parent.childCount()):
                child = parent.child(i)
                if child.data(0, Qt.ItemDataRole.UserRole) == ('Units', scope):
                    return child
                found = matching_item(child)
                if found is not None:
                    return found
            return None
        target = None
        for i in range(self.navigation.topLevelItemCount()):
            target = matching_item(self.navigation.topLevelItem(i))
            if target is not None:
                break
        if target is None:
            return
        self.search.clear()
        self.navigation.setCurrentItem(target)
        for index, record in enumerate(self.visible_rows):
            if record.get('id') == unit_id:
                self.grid.selectRow(index)
                self.grid.scrollToItem(self.grid.item(index, 0))
                break

    def inspect(self):
        row = self.grid.currentRow()
        if self.document is None or row < 0 or row >= len(self.visible_rows):
            return
        element = self.visible_rows[row]
        self.selected_element = element
        self.update_detail_tabs(element)
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
        self.overview.setPlainText(record_overview(self.group, element, doc))
        self.raw_xml.setPlainText(formatted_record_xml(element))


def main():
    app = QApplication(sys.argv)
    # Phase 1 readability baseline: point size remains DPI-aware under Windows.
    font = app.font()
    font.setPointSize(11)
    app.setFont(font)
    window = QtExplorer()
    window.show()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
