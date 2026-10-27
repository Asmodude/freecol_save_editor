"""Qt explorer with Phase 2B staged editing; launch with py qt_readonly.py.

Only explicitly supported fields are editable. Staged values never mutate
source XML; export uses the established safe producer.
"""
import sys
import os
from time import perf_counter
from pathlib import Path
from xml.etree.ElementTree import Element

from PySide6.QtCore import Qt, QSize, QSettings, QSortFilterProxyModel
from PySide6.QtGui import QFont, QBrush, QPixmap, QIcon
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QDialog,
    QMessageBox, QPushButton, QSplitter, QTabWidget, QTableWidget,
    QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator, QVBoxLayout,
    QWidget, QPlainTextEdit, QGroupBox, QHeaderView, QSizePolicy, QStyle, QDockWidget
)
from save_document import SaveDocument
from edit_session import EditSession, EditValidationError
from edit_preflight import stage_checked
from qt_staged_changes_panel import StagedChangesPanel
import presentation
from qt_navigation import rows_for_scope, human_player_id
from qt_navigation_lookup import find_navigation_item
from qt_navigation_builder import NavigationBuilderMixin
from qt_global_search_ui import GlobalSearchMixin
from qt_diplomacy_view import DiplomacyViewMixin
from qt_founding_fathers_view import FoundingFathersViewMixin
from qt_workspace_header_view import WorkspaceHeaderMixin
from qt_detail_tabs_view import DetailTabsMixin
from qt_record_table_model import RecordTableModel
from qt_record_sort_proxy import RecordSortFilterProxy
from qt_record_table_view import build_record_table_view, apply_record_view_sizing, selected_source_record, select_record_in_view
from qt_colony_details import colony_sections, colony_detail_nodes
from qt_settlement_details import settlement_units
from qt_overview import record_overview
from qt_overview_panel import OverviewPanel
from qt_inspector_details import InspectorDetails
from qt_final_visual_format import established_turn, colony_inspector_location
from qt_unit_icons import UnitIcons
from colony_graphics import resolve_colony_graphic
from qt_detail_inspector import detail_inspection
from qt_raw_xml import formatted_record_xml
from qt_display import display_row
from qt_sorting import NUMERIC_COLUMNS, NUMERIC_DETAIL_COLUMNS, sort_key
from qt_father_portraits import FatherPortraits
from qt_founding_fathers import father_source_node
from qt_national_goods import colony_goods_breakdown, transported_goods_breakdown
from qt_unit_groups import unit_groups, unit_group_scope
from qt_game_properties import game_property_rows, game_property_source
from qt_property_display import compact_property_value
from qt_global_search import global_results
from qt_diplomacy import settlement_alarm_rows
from qt_navigation_icons import NavigationIcons
from qt_flag_icons import flag_icon, flag_pixmap
from qt_goods_icons import GoodsIcons
from qt_workspace_header import workspace_identity
from qt_save_directory import save_directory
from qt_about_dialog import AboutDialog
from freecol_art_source import set_installation_root, validate_installation, configured_root

GROUPS = ('Players', 'Colonies', 'Native settlements', 'Units', 'Founding Fathers', 'National Goods', 'Game properties', 'Diplomacy')
HEADERS = {
    'Players': ('ID','Username','Nation','Type','Colonies','Settlements','Gold','Tax','Score','AI','Dead'),
    'Colonies': ('ID','Name','Owner','Location','Established','Liberty','Sons of Liberty','Production bonus'),
    'Native settlements': ('ID','Name','Owner','Location','Learnable skill','Wanted goods'),
    'Units': ('ID','Type','Owner','Location','Role','Experience toward','Experience','Moves left','Max moves','Hit points','State'),
    'Founding Fathers': ('Founding Father', 'Status'),
    'National Goods': ('Goods', 'Source → proposed total', 'Colonies with source stock'),
    'Game properties': ('Source', 'Property', 'Saved value'),
    'Diplomacy': ('Category', 'Other nation', 'Relationship', 'Saved value'),
}



class QtExplorer(DetailTabsMixin, WorkspaceHeaderMixin, FoundingFathersViewMixin, DiplomacyViewMixin, GlobalSearchMixin, NavigationBuilderMixin, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FreeCol Save Editor — Qt staged editing')
        self.resize(1450, 875)
        self.document = None
        self.session = EditSession()
        self.group = 'Players'
        self.scope = 'mine'
        self.visible_rows = []
        # Staged migration: mirror displayed records in a real Qt model while
        # keeping the accepted QTableWidget UI unchanged until parity is proven.
        self.record_model = RecordTableModel()
        self.record_proxy = RecordSortFilterProxy(self)
        self.record_proxy.setSourceModel(self.record_model)
        self.record_proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.record_proxy.setFilterKeyColumn(-1)
        self.selected_element = None
        self.detail_unit_id = None
        self.detail_nodes = {}
        self.breakdown_target = None
        self.art_settings = QSettings('FreeColSaveEditor', 'QtPreview')
        saved_art_root = self.art_settings.value('freecol_installation', '', type=str)
        set_installation_root(saved_art_root if saved_art_root and validate_installation(saved_art_root)[0] else None)
        self.father_portraits = FatherPortraits()
        self.navigation_icons = NavigationIcons()
        self.goods_icons = GoodsIcons()
        self.unit_icons = UnitIcons()
        self.recruiting_father = None
        self.offered_fathers = []

        settings_menu = self.menuBar().addMenu('File')
        settings_menu.addAction('FreeCol installation…', self.choose_freecol_installation)
        settings_menu.addAction('Use automatic artwork discovery', self.reset_freecol_installation)
        settings_menu.addSeparator()
        settings_menu.addAction('Open Save…', self.open_save)
        settings_menu.addAction('Save As…', self.save_as)
        settings_menu.addAction('Exit', self.close)
        help_menu = self.menuBar().addMenu('Help')
        help_menu.addAction('About FreeCol Save Editor…', self.show_about)

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
        self.save_button = QPushButton('Save As (0)')
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_as)
        self.global_button = QPushButton('Search all…')
        self.global_button.clicked.connect(self.open_global_search)
        self.global_button.setEnabled(False)
        self.map_button = QPushButton('Open Map Editor')
        self.map_button.setEnabled(False)
        self.map_button.setToolTip(
            'The existing Map Editor is available in the Tkinter application. '
            'The Qt map will be integrated in Phase 3.')
        self.heading = QLabel('Open a FreeCol save to begin · Safe staged editing')
        toolbar.addWidget(self.open_button)
        toolbar.addWidget(self.save_button)
        toolbar.addWidget(self.global_button)
        toolbar.addWidget(self.map_button)
        toolbar.addWidget(self.heading, 1)
        layout.addWidget(toolbar_widget, 0)
        self.editing_instructions = QLabel('To make edits: Edit data one at a time followed by clicking "Stage Change" next to that edit.')
        self.editing_instructions.setObjectName('editingInstructions')
        self.editing_instructions.setWordWrap(True)
        layout.addWidget(self.editing_instructions, 0)


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
        self.workspace_header = QWidget()
        header_layout = QHBoxLayout(self.workspace_header)
        header_layout.setContentsMargins(7, 8, 7, 9)
        header_layout.setSpacing(13)
        self.workspace_emblem = QLabel()
        self.workspace_emblem.setFixedSize(66, 52)
        self.workspace_emblem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.workspace_emblem)
        header_text = QWidget()
        header_text_layout = QVBoxLayout(header_text)
        header_text_layout.setContentsMargins(0, 0, 0, 0)
        header_text_layout.setSpacing(3)
        self.workspace_title = QLabel('Savegame Explorer')
        title_font = QFont(self.workspace_title.font())
        title_font.setBold(True)
        title_font.setPointSize(max(14, title_font.pointSize() + 3))
        self.workspace_title.setFont(title_font)
        self.workspace_subtitle = QLabel('Open a FreeCol save to begin')
        self.workspace_subtitle.setStyleSheet('color: palette(mid);')
        header_text_layout.addWidget(self.workspace_title)
        header_text_layout.addWidget(self.workspace_subtitle)
        header_layout.addWidget(header_text, 1)
        self.search = QLineEdit()
        self.search.setFixedWidth(230)
        self.search.setPlaceholderText('Filter visible rows…')
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.populate)
        header_layout.addWidget(self.search)
        center_layout.addWidget(self.workspace_header)
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
        self.workspace_splitter = QSplitter(Qt.Orientation.Vertical)
        self.workspace_table_area = QWidget()
        table_area_layout = QVBoxLayout(self.workspace_table_area)
        table_area_layout.setContentsMargins(0, 0, 0, 0)
        table_area_layout.setSpacing(0)
        self.model_view = build_record_table_view(self.record_proxy, self.workspace_table_area)
        self.model_view.selectionModel().currentChanged.connect(
            lambda current, previous: self.inspect())
        table_area_layout.addWidget(self.model_view, 1)
        self.diplomacy_tabs = QTabWidget()
        self.diplomacy_grids = {}
        for category in ('Rival Nations', 'Natives'):
            table = QTableWidget()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(('Nation / Leader', 'Stance', 'Tension'))
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            table.setAlternatingRowColors(True)
            table.setSortingEnabled(True)
            table.itemSelectionChanged.connect(lambda category=category: self.inspect_diplomacy(category))
            self.diplomacy_grids[category] = table
            self.diplomacy_tabs.addTab(table, category)
        table_area_layout.addWidget(self.diplomacy_tabs, 1)
        self.diplomacy_tabs.hide()

        self.tabs = QTabWidget()
        self.overview = OverviewPanel()
        self.tabs.addTab(self.overview, 'Overview')
        self.overview.edit_requested.connect(self.stage_overview_edit)
        self.overview.equipment_requested.connect(self.stage_unit_equipment)
        self.overview.skill_requested.connect(self.stage_native_skill)
        self.colony_tables = {}
        for name in ('Buildings', 'Workers', 'Stationed units', 'Goods', 'Affiliated units', 'Alarm', 'By colony', 'In transit'):
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
        self.workspace_splitter.addWidget(self.workspace_table_area)
        self.workspace_splitter.addWidget(self.tabs)
        self.workspace_splitter.setChildrenCollapsible(False)
        self.workspace_splitter.setHandleWidth(7)
        self.workspace_splitter.setStretchFactor(0, 3)
        self.workspace_splitter.setStretchFactor(1, 2)
        self.workspace_splitter.setSizes([480, 320])
        center_layout.addWidget(self.workspace_splitter, 1)
        panes.addWidget(center)

        inspector = QWidget()
        inspector_layout = QVBoxLayout(inspector)
        inspector_layout.addWidget(QLabel('Inspector — original/source save values'))
        self.inspector_source_notice = QLabel('Details and Raw XML show the opened save, excluding staged changes. For example, a unit staged as Pioneer with 100 tools may still show source role=model.role.default and roleCount=0. Proposed values are listed in Staged Changes and written only by Save As.')
        self.inspector_source_notice.setObjectName('inspectorSourceNotice')
        self.inspector_source_notice.setWordWrap(True)
        inspector_layout.addWidget(self.inspector_source_notice)
        self.inspector_label = QLabel('Select an individual row to inspect its attributes.')
        self.inspector_label.setWordWrap(True)
        inspector_layout.addWidget(self.inspector_label)
        self.details = InspectorDetails()
        self.inspector_tabs = QTabWidget()
        self.inspector_tabs.addTab(self.details, 'Details (source)')
        self.raw_xml = QPlainTextEdit()
        self.raw_xml.setReadOnly(True)
        self.inspector_tabs.addTab(self.raw_xml, 'Raw XML (source)')
        inspector_layout.addWidget(self.inspector_tabs, 1)
        self.jump_colony_button = QPushButton('Open colony Goods →')
        self.jump_colony_button.setEnabled(False)
        self.jump_colony_button.hide()
        self.jump_colony_button.clicked.connect(self.open_breakdown_colony)
        inspector_layout.addWidget(self.jump_colony_button)
        self.jump_unit_button = QPushButton('Open full unit record →')
        self.jump_unit_button.setEnabled(False)
        self.jump_unit_button.hide()
        self.jump_unit_button.clicked.connect(self.open_detail_unit)
        inspector_layout.addWidget(self.jump_unit_button)
        self.unit_xml_button = QPushButton('View selected unit XML →')
        self.unit_xml_button.hide()
        self.unit_xml_button.clicked.connect(
            lambda: self.inspector_tabs.setCurrentWidget(self.raw_xml))
        inspector_layout.addWidget(self.unit_xml_button)
        self.inspector_hint = QLabel('Supported numeric values can be staged from Overview and colony Workers')
        inspector_layout.addWidget(self.inspector_hint)
        self.right_splitter = QSplitter(Qt.Orientation.Vertical)
        self.right_splitter.setObjectName('inspectorPendingSplitter')
        self.right_splitter.addWidget(inspector)
        self.pending_panel = StagedChangesPanel(self.session)
        self.pending_panel.setObjectName('stagedChangesRightPanel')
        self.pending_panel.changed.connect(self.refresh_staged_view)
        self.right_splitter.addWidget(self.pending_panel)
        self.right_splitter.setStretchFactor(0, 3)
        self.right_splitter.setStretchFactor(1, 2)
        self.right_splitter.setSizes([530, 240])
        panes.addWidget(self.right_splitter)
        panes.setChildrenCollapsible(False)
        panes.setSizes([240, 885, 325])
        layout.addWidget(panes, 1)
        self.update_save_button()

        self.statusBar().showMessage(
            'Safe staged editing · Map Editor remains in Tkinter')
        self.install_navigation()

    def stage_overview_edit(self, record_id, field, raw_value):
        if self.document is None:
            return
        player_field = field in ('gold', 'tax')
        unit_field = field in ('experience', 'movesLeft')
        colony_field = field == 'sonsOfLibertyTarget'
        if not (player_field or unit_field or colony_field):
            return
        element = (self.document.players.get(record_id) if player_field
                   else next((colony for colony in self.document.colonies
                              if colony.get('id') == record_id), None) if colony_field
                   else self.document.unit_by_id(record_id))
        group = 'Players' if player_field else 'Colonies' if colony_field else 'Units'
        if element is None or (not colony_field and field not in EditSession.editable_fields(group, element)):
            return
        if player_field and field == 'tax' and (element.get('playerType', '').lower() in ('native', 'indian') or element.get('gold') == '-2147483648'):
            return
        raw_original = element.get('sonsOfLiberty' if colony_field else field)
        if not raw_original or not raw_original.isascii() or not raw_original.isdecimal():
            return
        original = int(raw_original)
        key = (record_id, field)
        try:
            # Backend preflight evaluates movesLeft against any staged role,
            # whereas the existing EditSession numeric check uses source role.
            if field == 'movesLeft':
                raw = raw_value.strip()
                if not raw.isascii() or not raw.isdecimal():
                    raise EditValidationError('Invalid movement: enter a non-negative whole number.')
                new = int(raw)
            else:
                new = self.session.validate(key, raw_value, original=original)
            stage_checked(self.session, self.document.xml_bytes, key, original, new)
        except (EditValidationError, ValueError) as exc:
            QMessageBox.warning(self, 'Cannot stage ' + field, str(exc))
            return
        self.refresh_staged_view()

    def stage_relation(self, owner_id, field, raw_value):
        """Validate real saved relationship before stage; never create missing edges."""
        if self.document is None or '|' not in field:
            return
        kind, other_id = field.split('|', 1)
        if kind not in ('stance', 'tension', 'alarm'):
            return
        if kind == 'alarm':
            owner = next((s for s in self.document.native_settlements if s.get('id') == owner_id), None)
        else:
            owner = self.document.players.get(owner_id)
        if owner is None or other_id not in self.document.players:
            return
        relations = [r for r in owner.findall(kind) if r.get('player') == other_id]
        if len(relations) != 1:
            QMessageBox.warning(self, 'Cannot stage relationship', 'Relationship absent or not unique in original save')
            return
        previous = relations[0].get('value')
        if previous is None:
            return
        key = (owner_id, field)
        try:
            original = previous if kind == 'stance' else int(previous)
            new = self.session.validate(key, str(raw_value), original=original)
            stage_checked(self.session, self.document.xml_bytes, key, original, new)
        except (ValueError, EditValidationError) as exc:
            QMessageBox.warning(self, 'Cannot stage relationship', str(exc))
            return
        self.refresh_staged_view()

    def stage_native_skill(self, settlement_id, skill):
        if self.document is None or skill not in self.document.professions:
            return
        settlement = next((item for item in self.document.native_settlements
                           if item.get('id') == settlement_id), None)
        if settlement is None or settlement.get('learnableSkill') is None:
            return
        key = (settlement_id, 'learnableSkill')
        original = settlement.get('learnableSkill')
        try:
            proposed = self.session.validate(key, skill, original=original,
                                             professions=self.document.professions)
            stage_checked(self.session, self.document.xml_bytes, key, original, proposed)
        except (ValueError, EditValidationError) as exc:
            QMessageBox.warning(self, 'Cannot stage skill', str(exc))
            return
        self.refresh_staged_view()

    def stage_colony_goods(self, colony_id, goods_type, raw_value):
        """Edit a specific warehouse type identified by its full ruleset ID."""
        if self.document is None:
            return
        colony = next((node for node in self.document.colonies
                       if node.get('id') == colony_id), None)
        if colony is None or goods_type not in self.document.goods_types:
            return
        stored = colony.find('./goodsContainer/storedGoods')
        if stored is None:
            QMessageBox.warning(self, 'Cannot stage goods', 'Colony has no storedGoods element')
            return
        found = [g for g in stored.findall('goods') if g.get('type') == goods_type]
        if len(found) > 1:
            QMessageBox.warning(self, 'Cannot stage goods', 'Duplicated goods type in colony')
            return
        original = int(found[0].get('amount')) if found else 0
        key = (colony_id, goods_type)
        try:
            new = self.session.validate(key, raw_value, original=original)
            stage_checked(self.session, self.document.xml_bytes, key, original, new)
        except (ValueError, TypeError, EditValidationError) as exc:
            QMessageBox.warning(self, 'Cannot stage goods', str(exc))
            return
        self.refresh_staged_view()

    def stage_unit_equipment(self, unit_id, role, count):
        """Stage composite equipment through the shared backend preflight."""
        if self.document is None:
            return
        unit = self.document.unit_by_id(unit_id)
        if unit is None or role is None:
            return
        from equipment_rules import validate_equipment
        if role == 'model.role.default': count = 0
        original = (unit.get('role', 'model.role.default'), int(unit.get('roleCount', '1')))
        try:
            if (unit_id, 'deleteUnit') in self.session.edits or any(
                    k[1] == 'deleteNativeUnit' and k[0].split('|')[0] == unit_id
                    for k in self.session.edits):
                raise ValueError('Unit already staged for deletion')
            validate_equipment(self.document.root, unit, role, count)
            from edit_backend import proportional_movement
            from edit_preflight import preflight
            from movement_rules import movement_cap
            from xml.etree.ElementTree import Element
            old_cap = movement_cap(self.document.root, Element('unit',
                               dict(unit.attrib, role=original[0], roleCount=str(original[1]))))
            prior_role = self.session.staged_value((unit_id, 'equipment'), original)[0]
            prior_cap = movement_cap(self.document.root, Element('unit',
                               dict(unit.attrib, role=prior_role)))
            new_cap = movement_cap(self.document.root, Element('unit',
                               dict(unit.attrib, role=role)))
            move_key = (unit_id, 'movesLeft')
            proposed = dict(self.session.edits)
            if (role, count) != original:
                proposed[(unit_id, 'equipment')] = (original, (role, count))
            else:
                proposed.pop((unit_id, 'equipment'), None)
            if move_key in proposed:
                move_original, move_current = proposed[move_key]
                # Returning to the source role should also restore a source-equal
                # explicit movement override. Do not scale 3/12 down to 1/3
                # when the user explicitly requested the original 3 MP.
                if (role, count) == original and move_current == move_original:
                    proposed.pop(move_key)
                else:
                    recalculated = proportional_movement(move_current, prior_cap, new_cap)
                    if recalculated == move_original and (role, count) == original:
                        proposed.pop(move_key)
                    else:
                        proposed[move_key] = (move_original, recalculated)
            preflight(self.document.xml_bytes, proposed)
            self.session.edits.clear()
            self.session.edits.update(proposed)
        except (ValueError, TypeError) as exc:
            QMessageBox.warning(self, 'Cannot stage equipment', str(exc))
            return
        self.refresh_staged_view()

    def refresh_staged_view(self):
        self.pending_panel.refresh()
        self.update_save_button()
        if self.document is not None:
            chosen = self.selected_element
            if self.group == 'Diplomacy':
                active_category = self.diplomacy_tabs.tabText(self.diplomacy_tabs.currentIndex())
                self.populate()
                for category, table in self.diplomacy_grids.items():
                    if chosen is None:
                        continue
                    for row in range(table.rowCount()):
                        item = table.item(row, 0)
                        record = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
                        if record is not None and (record.get('owner'), record.get('other')) == (
                                chosen.get('owner'), chosen.get('other')):
                            table.selectRow(row)
                            break
                for index in range(self.diplomacy_tabs.count()):
                    if self.diplomacy_tabs.tabText(index) == active_category:
                        self.diplomacy_tabs.setCurrentIndex(index)
                        break
                self.inspect_diplomacy(active_category)
                return
            active_tab = self.tabs.tabText(self.tabs.currentIndex()) if self.tabs.currentIndex() >= 0 else None
            self.populate()
            if chosen is not None:
                select_record_in_view(self.model_view, self.record_model, chosen)
                self.inspect()
                if active_tab:
                    for index in range(self.tabs.count()):
                        if self.tabs.tabText(index) == active_tab:
                            self.tabs.setCurrentIndex(index)
                            break

    def update_save_button(self):
        self.save_button.setText(f'Save As ({self.session.count})')
        if self.session.has_unexported_changes:
            self.save_button.setToolTip('Current staged changes differ from last successful export')
        elif self.session.exported_path is not None:
            self.save_button.setToolTip(f'Changes exported to {self.session.exported_path}; edits remain staged')
        else:
            self.save_button.setToolTip('Export staged changes to a new savegame')
        self.save_button.setEnabled(self.document is not None and self.session.count > 0)

    def confirm_discard(self):
        if not self.session.has_unexported_changes:
            return True
        response = QMessageBox.question(
            self, 'Unexported changes',
            ('Your current changes differ from the last exported save. '
             'Discard those differences?' if self.session.exported_path is not None
             else f'Discard {self.session.count} unexported staged changes?'),
            QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel)
        return response == QMessageBox.StandardButton.Discard

    def closeEvent(self, event):
        if not self.confirm_discard():
            event.ignore()
            return
        super().closeEvent(event)

    def save_as(self):
        if self.document is None or not self.session.count:
            return
        source = Path(self.document.path)
        candidate = source.with_name(source.stem + '_edited.fsg')
        suffix = 2
        while candidate.exists():
            candidate = source.with_name(f'{source.stem}_edited_{suffix}.fsg')
            suffix += 1
        destination, _ = QFileDialog.getSaveFileName(
            self, 'Export edited FreeCol save', str(candidate),
            'FreeCol saves (*.fsg)', options=QFileDialog.Option.DontConfirmOverwrite)
        if not destination:
            return
        try:
            self.session.save_as(source, destination)
        except Exception as exc:
            QMessageBox.warning(self, 'Export refused', str(exc))
            return
        self.update_save_button()
        QMessageBox.information(
            self, 'Export complete',
            f'Exported {self.session.count} changes to {destination}. '
            'Edits remain staged against the original opened save.')

    @staticmethod
    def _read_only_note(message):
        label = QLabel(message)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        return label

    def _default_save_directory(self):
        return save_directory(previous=self.art_settings.value('last_save_directory', '', type=str))

    def show_about(self):
        AboutDialog(self).exec()

    def open_save(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Open FreeCol save', str(self._default_save_directory()),
            'FreeCol saves (*.fsg);;ZIP archives (*.zip);;All files (*)')
        if not path:
            return
        if not self.confirm_discard():
            return
        started = perf_counter()
        try:
            document = SaveDocument.load(path)
        except Exception as exc:
            QMessageBox.critical(self, 'Could not open save', str(exc))
            return
        loaded_at = perf_counter()
        self.art_settings.setValue('last_save_directory', str(Path(path).parent))
        self.document = document
        self.session = EditSession()
        self.pending_panel.session = self.session
        self.pending_panel.document = document
        self.pending_panel.refresh()
        self.update_save_button()
        self.global_button.setEnabled(True)
        self.install_navigation()
        navigation_at = perf_counter()
        self.heading.setText(f'{Path(path).name} · Turn {document.turn} · staged editing')
        # install_navigation() selects Overview and already triggers populate().
        if os.environ.get('FREECOL_QT_PROFILE') == '1':
            print(f'Qt load stages: parse/index={loaded_at-started:.3f}s; '
                  f'navigation+overview={navigation_at-loaded_at:.3f}s; '
                  f'total={navigation_at-started:.3f}s', flush=True)
        self.statusBar().showMessage(
            f'{len(document.players)} players · {len(document.colonies)} colonies · '
            f'{len(document.native_settlements)} native settlements · {len(document.units)} units'
            ' · Qt staged gold editing; Map Editor in Tkinter')

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
            select_record_in_view(self.model_view, self.record_model, self.visible_rows[0])

    def choose_freecol_installation(self):
        folder = QFileDialog.getExistingDirectory(
            self, 'Locate FreeCol installation', str(configured_root() or Path.home()))
        if not folder:
            return
        valid, message = validate_installation(folder)
        if not valid:
            QMessageBox.warning(self, 'FreeCol artwork not found', message)
            return
        set_installation_root(folder)
        self.art_settings.setValue('freecol_installation', folder)
        self.refresh_artwork()
        QMessageBox.information(self, 'FreeCol artwork', message)

    def reset_freecol_installation(self):
        self.art_settings.remove('freecol_installation')
        set_installation_root(None)
        self.refresh_artwork()

    def refresh_artwork(self):
        """Invalidate existing caches and redraw visible artwork."""
        self.navigation_icons = NavigationIcons()
        self.goods_icons = GoodsIcons()
        self.unit_icons = UnitIcons()
        self.overview.goods_icons = GoodsIcons()
        self.overview.unit_icons = UnitIcons()
        self.details._units = UnitIcons()
        if self.document is not None:
            target = (self.group, self.scope)
            self.install_navigation()
            iterator = QTreeWidgetItemIterator(self.navigation)
            while iterator.value():
                item = iterator.value()
                if item.data(0, Qt.ItemDataRole.UserRole) == target:
                    self.navigation.setCurrentItem(item)
                    break
                iterator += 1
            self.populate()
            self.overview._render()
            self.details._render()

    def national_goods_projection(self, record):
        """Source and proposed totals, without changing the original save."""
        source = int(record.get('amount', '0'))
        owner = record.get('owner')
        kind = record.get('id')
        ids = {col.get('id') for col in self.document.colonies if col.get('owner') == owner}
        delta = sum(int(new_value) - int(old_value)
                    for (record_id, field), (old_value, new_value) in self.session.edits.items()
                    if record_id in ids and field == kind)
        return source, source + delta, delta != 0

    def populate(self):
        self.update_workspace_header()
        # Apply category sizing even when no save is loaded and populate exits early.
        apply_record_view_sizing(self.model_view, self.group)
        self.record_proxy.set_record_group(self.group)
        is_diplomacy = self.group == 'Diplomacy'
        self.model_view.setVisible(not is_diplomacy)
        self.diplomacy_tabs.setVisible(is_diplomacy)
        self.visible_rows = []
        self.record_model.replace_rows((), HEADERS[self.group])
        self.selected_element = None
        self.detail_unit_id = None
        self.jump_unit_button.setEnabled(False)
        self.jump_unit_button.hide()
        self.unit_xml_button.hide()
        self.jump_colony_button.setEnabled(False)
        self.jump_colony_button.hide()
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
        doc = self.document
        if doc is None:
            return
        query = self.search.text().strip().casefold()
        if is_diplomacy:
            self.populate_diplomacy(query)
            return
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
        for element in (game_property_rows(doc) if self.group == 'Game properties' else rows_for_scope(doc, self.group, self.scope)):
            if self.group == 'Founding Fathers' and element.get('status') != 'Recruited':
                continue
            values = ((element.get('category'), element.get('nation'), element.get('kind'), element.get('value'))
                      if self.group == 'Diplomacy' else
                      (element.get('source'), element.get('name'), element.get('value'))
                      if self.group == 'Game properties' else
                      (element.get('name'), element.get('status'))
                      if self.group == 'Founding Fathers' else
                      (element.get('name'),
                       (f'{self.national_goods_projection(element)[0]} → {self.national_goods_projection(element)[1]}'
                        if self.national_goods_projection(element)[2] else element.get('amount')),
                       element.get('colonies'))
                      if self.group == 'National Goods' else
                      display_row(self.group, presentation.row_values(self.group, element, doc, self.session)))
            if query and query not in ' '.join(str(value) for value in values).casefold():
                continue
            rows.append((element, values))
        self.record_model.replace_rows(rows, HEADERS[self.group])
        self.visible_rows = [element for element, _ in rows]
        if self.group == 'Founding Fathers':
            self.congress_heading.setText('Continental Congress — ' + str(len(rows)) + ' recruited')
        model_decorations = {}
        model_tooltips = {}
        staged_cells = set()
        role_cells = set()
        for row, (record, values) in enumerate(rows):
            for col, value in enumerate(values):
                icon = QIcon()
                tooltip = None
                field_id = ({6: 'gold', 7: 'tax'}.get(col) if self.group == 'Players'
                            else {6: 'experience', 7: 'movesLeft'}.get(col) if self.group == 'Units'
                            else None)
                if field_id and self.session.is_changed((record.get('id'), field_id)):
                    staged_cells.add((row, col))
                    tooltip = ('STAGED ' + field_id + ': ' + str(value) +
                               ' (original save: ' + str(record.get(field_id)) + ')')
                if col == 0 and self.group != 'Founding Fathers':
                    row_kinds = {
                        'Players': 'nation', 'Colonies': 'colony',
                        'Native settlements': 'settlements', 'Units': 'units',
                        'National Goods': 'goods', 'Game properties': 'options',
                    }
                    kind = row_kinds.get(self.group)
                    if kind:
                        if self.group == 'Players':
                            nation_id = record.get('nationId') or record.get('nation')
                            native = record.get('playerType') in ('native', 'indian')
                            flag = flag_icon(nation_id, 15) if not native else QIcon()
                            icon = flag if not flag.isNull() else self.navigation_icons.icon(
                                kind, nation_id=nation_id, native=native, size=20)
                        elif self.group == 'Units':
                            effective_role = self.session.staged_value(
                                (record.get('id'), 'equipment'),
                                (record.get('role', 'model.role.default'), 0))[0]
                            icon = self.unit_icons.effective_icon(record.get('unitType'), effective_role)
                            if icon.isNull():
                                icon = self.navigation_icons.icon('units', size=20)
                        elif self.group == 'National Goods':
                            icon = self.goods_icons.icon(record.get('id') or record.get('name'))
                            if icon.isNull():
                                icon = self.navigation_icons.icon(kind, size=20)
                        elif self.group == 'Colonies':
                            art = resolve_colony_graphic(record)
                            image = QPixmap(str(art.image_path)) if art.image_path else QPixmap()
                            icon = (QIcon(image.scaled(
                                32, 30, Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation))
                                if not image.isNull() else self.navigation_icons.icon('colony', size=22))
                        else:
                            icon = self.navigation_icons.icon(kind, size=20)
                if self.group == 'Units' and col == 4:
                    actual_role = record.get('role', 'model.role.default')
                    effective_role = self.session.staged_value(
                        (record.get('id'), 'equipment'), (actual_role, 0))[0]
                    if effective_role != 'model.role.default':
                        tooltip = ('Equipped role: ' + str(effective_role) +
                                   ' | Unit type: ' + str(record.get('unitType')) +
                                   (' | STAGED change' if effective_role != actual_role else ''))
                        if effective_role != actual_role:
                            staged_cells.add((row, col))
                        else:
                            role_cells.add((row, col))
                if self.group == 'Native settlements' and col == 5:
                    from qt_goods_icons import goods_key
                    names = [part.strip() for part in str(value or '').split(',')]
                    recognised = [name for name in names if goods_key(name)]
                    if recognised:
                        strip = QPixmap(20 * len(recognised), 20)
                        strip.fill(Qt.GlobalColor.transparent)
                        from PySide6.QtGui import QPainter
                        painter = QPainter(strip)
                        for position, good in enumerate(recognised):
                            painter.drawPixmap(position * 20, 0,
                                               self.goods_icons.icon(good, 20).pixmap(20, 20))
                        painter.end()
                        icon = QIcon(strip)
                if self.group == 'Game properties' and col == 2:
                    if compact_property_value(value) != str(value or ''):
                        tooltip = ('Long value shortened here. Select the row '
                                   'for its complete saved value.')
                if self.group == 'Founding Fathers' and col == 0:
                    data = self.father_portraits.get(record.get('id'))
                    if data:
                        pixmap = QPixmap()
                        if pixmap.loadFromData(data):
                            icon = QIcon(pixmap)
                if not icon.isNull():
                    model_decorations[(row, col)] = icon
                if tooltip:
                    model_tooltips[(row, col)] = tooltip
        self.record_model.set_presentation(model_decorations, model_tooltips, staged_cells, role_cells)
        apply_record_view_sizing(self.model_view, self.group)
        self.model_view.resizeColumnsToContents()
        context = self.navigation.currentItem().text(0) if self.navigation.currentItem() else self.scope
        note = ('Human player could not be uniquely identified; no player was guessed.\n' 
                if self.scope=='mine' and human_player_id(doc) is None else '')
        self.refresh_breakdown_action(self.tabs.currentIndex())
        self.overview.setPlainText(
            f'{context} · {self.group}: {len(rows)} displayed\n' + note +
            'Choose a row above to see its full read-only record here.\n'
            'The inspector on the right shows only the currently selected object.')
        # Accepted Phase 2A usability contract: a sole displayed record
        # must be selected and inspected without a redundant second click.
        # This also applies to filtered results, using authoritative identity.
        if len(rows) == 1:
            select_record_in_view(self.model_view, self.record_model, rows[0][0])

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
        destination = find_navigation_item(self.navigation, 'Colonies', scope)
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
        target = find_navigation_item(self.navigation, 'Units', scope)
        if target is None:
            return
        self.search.clear()
        self.navigation.setCurrentItem(target)
        if select_record_in_view(self.model_view, self.record_model, unit):
            self.model_view.scrollTo(self.model_view.currentIndex())

    def inspect(self):
        if self.document is None:
            return
        element = selected_source_record(self.model_view, self.record_model)
        if element is None or not any(record is element for record in self.visible_rows):
            return
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
            source, projected, pending = self.national_goods_projection(element)
            self.details.setPlainText(
                f'Goods: {name}\nSource warehouse total: {amount}\n'
                + (f'Proposed total with staged edits: {projected}\n' if pending else '') +
                f'Colonies with source stock: {count}\n'
                'Staged warehouse edits are excluded until exported and reopened.')
            self.overview.setPlainText(
                f'{name}\n\nOriginal save warehouse total: {amount}\n'
                + (f'Proposed total with staged edits: {projected}\n' if pending else '') +
                f'Colonies containing this good: {count}\n\n'
                'Table shows source → proposed totals wherever warehouse edits are staged.\n'
                'Read-only aggregate; cargo aboard units and ships is excluded.')
            self.raw_xml.setPlainText(
                'Computed aggregate from owned colony goodsContainer/storedGoods/goods.\n'
                'Select a colony Goods tab for authoritative source XML.')
            return
        self.selected_element = element
        self.update_detail_tabs(element)
        self.unit_xml_button.setVisible(self.group == 'Units')
        if self.group == 'Diplomacy':
            self.inspector_label.setText(element.get('nation'))
            self.details.setPlainText(f"Category: {element.get('category')}\nOther nation: {element.get('nation')}\nRelationship: {element.get('kind')}\nSaved value: {element.get('value')}")
            owner = self.document.players.get(element.get('owner'))
            self.raw_xml.setPlainText(formatted_record_xml(owner) if owner is not None else 'No source player')
            self.overview.setPlainText('Read-only diplomatic relationship from the owning player XML.')
            return
        if self.group == 'Game properties':
            source = element.get('source')
            name = element.get('name')
            value = element.get('value')
            self.inspector_label.setText(f'{source}: {name}')
            self.details.setPlainText(f'Source: {source}\nProperty: {name}\nSaved value: {value}')
            self.overview.setPlainText('Read-only metadata from the saved game XML.\nNo option values are inferred.')
            self.raw_xml.setPlainText(formatted_record_xml(game_property_source(self.document, element)) if element.get('path') else formatted_record_xml(Element('saved' + source, dict(game_property_source(self.document, element).attrib))))
            return
        label = element.get('name') or element.get('username') or element.get('id') or 'Record'
        self.inspector_label.setText(label)
        doc = self.document
        summary = [('Name', label), ('Category', self.group)]
        if self.group == 'Founding Fathers':
            summary.extend([('Status', element.get('status')),
                            ('FreeCol identifier', element.get('id'))])
        elif self.group == 'Players':
            summary.extend([('Nation', presentation.short(element.get('nationId'))),
                            ('Gold', str(self.session.staged_value((element.get('id'), 'gold'), element.get('gold')))), ('Tax', None if element.get('playerType', '').lower() in ('native', 'indian') or element.get('gold') == '-2147483648' else str(self.session.staged_value((element.get('id'), 'tax'), element.get('tax')))),
                            ('AI controlled', element.get('ai'))])
        elif self.group == 'Colonies':
            summary.extend([('Owner', doc.owner_name(element.get('owner'))),
                            ('Location', colony_inspector_location(element, doc)),
                            ('Established', established_turn(element.get('established'))),
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
        overview_text = record_overview(self.group, element, doc)
        if self.group == 'Players' and self.session.is_changed((element.get('id'), 'gold')):
            overview_text += f'\n\nStaged gold: {self.session.staged_value((element.get("id"), "gold"), element.get("gold"))} (source: {element.get("gold")})'
        self.overview.setPlainText(overview_text)
        self.overview.set_record(self.group, element, doc, self.session)
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
