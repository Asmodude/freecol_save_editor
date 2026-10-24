"""Phase 1: read-only PySide6 shell; launch independently with py qt_readonly.py.

The accepted Tkinter editor remains the only editor and map-rendering application.
No savegame mutation is possible from this Qt window.
"""
import sys
import os
from time import perf_counter
from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QBrush, QPixmap, QIcon
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
from qt_display import display_row
from qt_sorting import NUMERIC_COLUMNS, NUMERIC_DETAIL_COLUMNS, sort_key
from qt_father_portraits import FatherPortraits
from qt_founding_fathers import father_source_node
from qt_national_goods import colony_goods_breakdown, transported_goods_breakdown
from qt_unit_groups import unit_groups, unit_group_scope

GROUPS = ('Players', 'Colonies', 'Native settlements', 'Units', 'Founding Fathers', 'National Goods')
HEADERS = {
    'Players': ('ID','Username','Nation','Type','Colonies','Settlements','Gold','Tax','Score','AI','Dead'),
    'Colonies': ('ID','Name','Owner','Location','Established','Liberty','Sons of Liberty','Production bonus'),
    'Native settlements': ('ID','Name','Owner','Location','Learnable skill','Wanted goods'),
    'Units': ('ID','Type','Owner','Location','Role','Experience toward','Experience','Moves left','Max moves','Hit points','State'),
    'Founding Fathers': ('Founding Father', 'Status'),
    'National Goods': ('Goods', 'Total in colonies', 'Colonies with stock'),
}



class SortableItem(QTableWidgetItem):
    """Keep row identity attached to items during Qt sorting."""
    def __init__(self, value, numeric=False):
        super().__init__('' if value is None else str(value))
        self.numeric = numeric
        if numeric:
            self.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    def __lt__(self, other):
        return sort_key(self.text(), self.numeric) < sort_key(other.text(), self.numeric)


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
        self.breakdown_target = None
        self.father_portraits = FatherPortraits()
        self.recruiting_father = None
        self.offered_fathers = []

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
        self.father_banner = QWidget()
        banner_layout = QHBoxLayout(self.father_banner)
        banner_layout.setContentsMargins(6, 6, 6, 6)
        self.father_portrait = QLabel()
        self.father_portrait.setFixedSize(85, 100)
        self.father_portrait.setAlignment(Qt.AlignmentFlag.AlignCenter)
        banner_layout.addWidget(self.father_portrait)
        self.father_banner_text = QPushButton('No Founding Father currently being recruited')
        self.father_banner_text.setEnabled(False)
        self.father_banner_text.clicked.connect(self.inspect_recruiting_father)
        banner_layout.addWidget(self.father_banner_text, 1)
        center_layout.addWidget(self.father_banner)
        self.father_banner.hide()
        self.offered_banner = QLabel()
        self.offered_banner.setWordWrap(True)
        self.offered_banner.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        center_layout.addWidget(self.offered_banner)
        self.offered_banner.hide()
        self.father_section_spacing = QWidget()
        self.father_section_spacing.setFixedHeight(20)
        center_layout.addWidget(self.father_section_spacing)
        self.father_section_spacing.hide()
        self.congress_heading = QLabel('Continental Congress')
        congress_font = QFont(self.congress_heading.font())
        congress_font.setBold(True)
        self.congress_heading.setFont(congress_font)
        center_layout.addWidget(self.congress_heading)
        self.congress_heading.hide()
        self.grid = QTableWidget()
        self.grid.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.grid.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.grid.setAlternatingRowColors(True)
        self.grid.setSortingEnabled(True)
        self.grid.setIconSize(QSize(60, 65))
        self.grid.itemSelectionChanged.connect(self.inspect)
        center_layout.addWidget(self.grid, 3)

        self.tabs = QTabWidget()
        self.overview = QPlainTextEdit()
        self.overview.setReadOnly(True)
        self.tabs.addTab(self.overview, 'Overview')
        self.colony_tables = {}
        for name in ('Buildings', 'Workers', 'Stationed units', 'Goods', 'Affiliated units', 'By colony', 'In transit'):
            table = QTableWidget()
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            table.setAlternatingRowColors(True)
            table.setSortingEnabled(True)
            table.itemSelectionChanged.connect(lambda section=name: self.inspect_detail(section))
            if name == 'By colony':
                table.cellClicked.connect(lambda row, column: self.inspect_detail('By colony'))
            self.tabs.addTab(table, name)
            self.colony_tables[name] = table
        self.tab_widgets = {'Overview': self.overview, **self.colony_tables}
        self.tabs.currentChanged.connect(self.refresh_breakdown_action)
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
        self.jump_colony_button = QPushButton('Open colony Goods →')
        self.jump_colony_button.setEnabled(False)
        self.jump_colony_button.clicked.connect(self.open_breakdown_colony)
        inspector_layout.addWidget(self.jump_colony_button)
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
        self.navigation.setUpdatesEnabled(False)
        self.navigation.clear()
        # Resolve native theme icons only once per rebuild, not for every settlement.
        icon_types = {
            'nation': QStyle.StandardPixmap.SP_ComputerIcon,
            'section': QStyle.StandardPixmap.SP_DirIcon,
            'colony': QStyle.StandardPixmap.SP_FileIcon,
            'planned': QStyle.StandardPixmap.SP_FileDialogDetailedView,
        }
        icons = {kind: self.style().standardIcon(icon) for kind, icon in icon_types.items()}

        def entry(parent, label, group=None, scope=None, ready=True, kind='section'):
            item = QTreeWidgetItem([label])
            item.setIcon(0, icons['planned' if not ready else kind])
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

        def grouped_unit_entries(parent, owner):
            if not doc or not owner:
                return
            groups = unit_groups(doc, owner)
            colonies = [c for c in doc.colonies if c.get('owner') == owner and c.get('id')]
            for colony in sorted(colonies, key=lambda c:(c.get('name') or '').casefold()):
                key = ('colony', colony.get('id'))
                count = len(groups.get(key, ()))
                if count:
                    entry(parent, f"{colony.get('name') or colony.get('id')} ({count})",
                          'Units', unit_group_scope(owner, 'colony', colony.get('id')), kind='colony')
            for label, kind in (('Aboard ships', 'ship'), ('Other locations', 'other')):
                count = len(groups.get((kind, ''), ()))
                if count:
                    entry(parent, f'{label} ({count})', 'Units', unit_group_scope(owner, kind))
        
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
        my_units = entry(my, 'Units', 'Units', 'mine')
        grouped_unit_entries(my_units, own)
        entry(my, 'Goods', 'National Goods', 'mine')
        entry(my, 'Research', ready=False)
        entry(my, 'Founding Fathers', 'Founding Fathers', 'mine')
        entry(my, 'Player Options', ready=False)

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
                    rival_units = entry(rival, 'Units', 'Units', 'player:' + pid)
                    grouped_unit_entries(rival_units, pid)
                    entry(rival, 'Goods', 'National Goods', 'player:' + pid)
                    entry(rival, 'Research', ready=False)
                    entry(rival, 'Founding Fathers', 'Founding Fathers', 'player:' + pid)
                    entry(rival, 'Player Options', ready=False)
                elif player.get('playerType') in ('indian', 'native'):
                    label = presentation.readable(nation_id) or pid
                    native = entry(natives, label, kind='nation')
                    settlements = entry(native, 'Settlements', 'Native settlements', 'native-owner:' + pid)
                    for village in sorted((v for v in doc.native_settlements if v.get('owner') == pid),
                                          key=lambda v: (v.get('name') or '').casefold()):
                        if village.get('id'):
                            entry(settlements, village.get('name') or village.get('id'),
                                  'Native settlements', 'settlement-id:' + village.get('id'),
                                  kind='colony')
                    native_units = entry(native, 'Units', 'Units', 'player:' + pid)
                    grouped_unit_entries(native_units, pid)

        entry(None, 'Map', ready=False)
        entry(None, 'Game Options', ready=False)
        my.setExpanded(True)
        rivals.setExpanded(True)
        natives.setExpanded(True)
        self.navigation.blockSignals(False)
        self.navigation.setCurrentItem(overview)
        self.navigation.setUpdatesEnabled(True)

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
        started = perf_counter()
        try:
            document = SaveDocument.load(path)
        except Exception as exc:
            QMessageBox.critical(self, 'Could not open save', str(exc))
            return
        loaded_at = perf_counter()
        self.document = document
        self.install_navigation()
        navigation_at = perf_counter()
        self.heading.setText(f'{Path(path).name} · Turn {document.turn} · READ ONLY')
        # install_navigation() selects Overview and already triggers populate().
        if os.environ.get('FREECOL_QT_PROFILE') == '1':
            print(f'Qt load stages: parse/index={loaded_at-started:.3f}s; '
                  f'navigation+overview={navigation_at-loaded_at:.3f}s; '
                  f'total={navigation_at-started:.3f}s', flush=True)
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
        direct = (group == 'Colonies' and scope.startswith('colony-id:')) or (group == 'Native settlements' and scope.startswith('settlement-id:'))
        if direct:
            self.search.blockSignals(True)
            self.search.clear()
            self.search.blockSignals(False)
        self.populate()
        if direct and self.visible_rows:
            self.grid.selectRow(0)

    def populate(self):
        self.grid.setSortingEnabled(False)
        self.grid.setRowCount(0)
        self.grid.clearContents()
        self.visible_rows = []
        self.selected_element = None
        self.detail_unit_id = None
        self.jump_unit_button.setEnabled(False)
        self.jump_colony_button.setEnabled(False)
        self.breakdown_target = None
        self.breakdown_target = None
        self.details.clear()
        self.raw_xml.clear()
        self.inspector_label.setText('Select an individual row to inspect its attributes.')
        self.overview.clear()
        father_view = self.group == 'Founding Fathers' and self.document is not None
        self.father_banner.setVisible(father_view)
        self.congress_heading.setVisible(father_view)
        self.father_section_spacing.setVisible(father_view)
        self.offered_banner.setVisible(False)
        self.recruiting_father = None
        self.offered_fathers = []
        self.update_detail_tabs(None)
        self.grid.setColumnCount(len(HEADERS[self.group]))
        self.grid.setHorizontalHeaderLabels(HEADERS[self.group])
        doc = self.document
        if doc is None:
            self.grid.setSortingEnabled(True)
            return
        query = self.search.text().strip().casefold()
        if self.group == 'Founding Fathers':
            father_records = rows_for_scope(doc, self.group, self.scope)
            self.recruiting_father = next(
                (f for f in father_records if f.get('status') == 'Recruiting'), None)
            self.offered_fathers = [f for f in father_records if f.get('status') == 'Offered']
            offered = [f.get('name', '') for f in self.offered_fathers]
            father = self.recruiting_father
            if father is not None:
                self.father_banner_text.setText(
                    'CURRENTLY RECRUITING\n' + father.get('name', '') +
                    '\nIn progress · Select to inspect')
                self.father_banner_text.setEnabled(True)
                self._set_father_portrait(self.father_portrait, father.get('id'), 85, 100)
            else:
                self.father_banner_text.setText('No Founding Father currently being recruited')
                self.father_banner_text.setEnabled(False)
                self.father_portrait.clear()
                self.father_portrait.setText('No portrait')
            if offered:
                self.offered_banner.setText('Also offered (not recruited): ' + ', '.join(offered))
                self.offered_banner.setVisible(True)
        rows = []
        for element in rows_for_scope(doc, self.group, self.scope):
            if self.group == 'Founding Fathers' and element.get('status') != 'Recruited':
                continue
            values = ((element.get('name'), element.get('status'))
                      if self.group == 'Founding Fathers' else
                      (element.get('name'), element.get('amount'), element.get('colonies'))
                      if self.group == 'National Goods' else
                      display_row(self.group, presentation.row_values(self.group, element, doc, self.session)))
            if query and query not in ' '.join(str(value) for value in values).casefold():
                continue
            rows.append((element, values))
        self.visible_rows = [element for element, _ in rows]
        if self.group == 'Founding Fathers':
            self.congress_heading.setText('Continental Congress — ' + str(len(rows)) + ' recruited')
        self.grid.setRowCount(len(rows))
        for row, (_, values) in enumerate(rows):
            for col, value in enumerate(values):
                cell = SortableItem(value, HEADERS[self.group][col] in NUMERIC_COLUMNS[self.group])
                cell.setData(Qt.ItemDataRole.UserRole, row)
                cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if self.group == 'Founding Fathers' and col == 0:
                    data = self.father_portraits.get(rows[row][0].get('id'))
                    if data:
                        pixmap = QPixmap()
                        if pixmap.loadFromData(data):
                            cell.setIcon(QIcon(pixmap))
                    self.grid.setRowHeight(row, 75)
                self.grid.setItem(row, col, cell)
        self.grid.setSortingEnabled(True)
        self.grid.resizeColumnsToContents()
        context = self.navigation.currentItem().text(0) if self.navigation.currentItem() else self.scope
        note = ('Human player could not be uniquely identified; no player was guessed.\n' 
                if self.scope=='mine' and human_player_id(doc) is None else '')
        self.overview.setPlainText(
            f'{context} · {self.group}: {len(rows)} displayed\n' + note +
            'Choose a row above to see its full read-only record here.\n'
            'The inspector on the right shows only the currently selected object.')

    def _set_father_portrait(self, label, father_id, width, height):
        data = self.father_portraits.get(father_id)
        pixmap = QPixmap()
        if data and pixmap.loadFromData(data):
            label.setPixmap(pixmap.scaled(width, height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
        else:
            label.clear()
            label.setText('Portrait unavailable')

    def inspect_recruiting_father(self):
        if self.recruiting_father is not None:
            self.grid.clearSelection()
            self.inspect_father_record(self.recruiting_father)

    def inspect_father_record(self, element):
        self.selected_element = element
        self.update_detail_tabs(element)
        self.inspector_label.setText(element.get('name', 'Founding Father'))
        self.details.setPlainText(
            'Name: ' + element.get('name', '') + '\n' +
            'Category: Founding Fathers\n' +
            'Status: ' + element.get('status', '') + '\n' +
            'FreeCol identifier: ' + element.get('id', ''))
        self.overview.setPlainText(record_overview('Founding Fathers', element, self.document))
        source = father_source_node(self.document, element)
        self.raw_xml.setPlainText(
            formatted_record_xml(source) if source is not None else
            'No matching source XML node found for this Founding Father.')

    def update_detail_tabs(self, element):
        self.detail_unit_id = None
        self.jump_unit_button.setEnabled(False)
        colony = element if self.group == 'Colonies' else None
        settlement = element if self.group == 'Native settlements' else None
        sections = colony_sections(colony, self.document) if colony is not None else {}
        self.detail_nodes = colony_detail_nodes(colony, self.document) if colony is not None else {}
        if settlement is not None:
            sections['Affiliated units'] = settlement_units(settlement, self.document)
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
            allowed.add('Affiliated units')
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
                    table.setItem(row, col, item)
            table.setSortingEnabled(True)
            table.resizeColumnsToContents()
            table.blockSignals(False)

    def refresh_breakdown_action(self, _index):
        """Synchronize the drill-down when the By colony tab becomes visible."""
        table = self.colony_tables['By colony']
        if (self.group != 'National Goods'
                or self.tabs.currentWidget() is not table
                or self.selected_element is None):
            return
        # Opening this tab is not a selection. Require an explicit colony click.
        self.jump_colony_button.setEnabled(bool(table.selectedItems()) and self.breakdown_target is not None)

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
            self.jump_colony_button.setEnabled(True)
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

    def open_breakdown_colony(self):
        target = self.breakdown_target
        if not target or self.document is None:
            return
        good_id, colony_name = target
        owner = self.selected_element.get('owner') if self.selected_element is not None else None
        matches = [colony for colony in self.document.colonies
                   if colony.get('owner') == owner
                   and (colony.get('name') or colony.get('id') or 'Unnamed colony') == colony_name]
        # Duplicate names must never cause an arbitrary navigation.
        if len(matches) != 1 or not matches[0].get('id'):
            return
        scope = 'colony-id:' + matches[0].get('id')
        def find_item(parent):
            for index in range(parent.childCount()):
                item = parent.child(index)
                if item.data(0, Qt.ItemDataRole.UserRole) == ('Colonies', scope):
                    return item
                found = find_item(item)
                if found is not None:
                    return found
            return None
        destination = None
        for index in range(self.navigation.topLevelItemCount()):
            destination = find_item(self.navigation.topLevelItem(index))
            if destination is not None:
                break
        if destination is None:
            return
        self.navigation.setCurrentItem(destination)
        table = self.colony_tables['Goods']
        self.tabs.setCurrentWidget(table)
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item is not None and item.text() == presentation.readable(good_id):
                table.selectRow(row)
                table.scrollToItem(item)
                break

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
                for display_row_index in range(self.grid.rowCount()):
                    cell = self.grid.item(display_row_index, 0)
                    if cell and cell.data(Qt.ItemDataRole.UserRole) == index:
                        self.grid.selectRow(display_row_index)
                        self.grid.scrollToItem(cell)
                        break
                break

    def inspect(self):
        row = self.grid.currentRow()
        if self.document is None or row < 0 or row >= len(self.visible_rows):
            return
        source_item = self.grid.item(row, 0)
        source_index = source_item.data(Qt.ItemDataRole.UserRole) if source_item else None
        if not isinstance(source_index, int) or source_index >= len(self.visible_rows):
            return
        element = self.visible_rows[source_index]
        if self.group == 'Founding Fathers':
            self.inspect_father_record(element)
            return
        if self.group == 'National Goods':
            self.selected_element = element
            self.update_detail_tabs(element)
            # The breakdown table is rebuilt with signals blocked. Select a
            # real colony afterwards so the inspector and action are live.
            self.breakdown_target = None
            self.jump_colony_button.setEnabled(False)
            name = element.get('name', 'Goods')
            amount = element.get('amount', '0')
            count = element.get('colonies', '0')
            self.inspector_label.setText(name)
            self.details.setPlainText(
                f'Goods: {name}\nTotal in colonies: {amount}\n'
                f'Colonies with stock: {count}')
            self.overview.setPlainText(
                f'{name}\n\nNation-wide colony warehouse total: {amount}\n'
                f'Colonies containing this good: {count}\n\n'
                'Read-only aggregate; cargo aboard units and ships is excluded.')
            self.raw_xml.setPlainText(
                'Computed aggregate from owned colony goodsContainer/storedGoods/goods.\n'
                'Select a colony Goods tab for authoritative source XML.')
            return
        self.selected_element = element
        self.update_detail_tabs(element)
        label = element.get('name') or element.get('username') or element.get('id') or 'Record'
        self.inspector_label.setText(label)
        doc = self.document
        summary = [('Name', label), ('Category', self.group)]
        if self.group == 'Founding Fathers':
            summary.extend([('Status', element.get('status')),
                            ('FreeCol identifier', element.get('id'))])
        elif self.group == 'Players':
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
        if self.group == 'Founding Fathers':
            self.raw_xml.setPlainText('Virtual read-only record. Membership is encoded in the owning player XML.\nSelect the player Overview to inspect the source XML.')
        else:
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
