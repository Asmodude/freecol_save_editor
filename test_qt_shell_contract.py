"""Phase 1 Qt module static checks that do not require PySide6 on CI."""
import ast
import unittest
from pathlib import Path


class QtShellContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (Path(__file__).resolve().parent / 'qt_readonly.py').read_text(encoding='utf-8')
        cls.tree = ast.parse(cls.source)
        cls.detail_source = (Path(__file__).resolve().parent / 'qt_detail_tabs_view.py').read_text(encoding='utf-8')
        cls.global_search_source = (Path(__file__).resolve().parent / 'qt_global_search_ui.py').read_text(encoding='utf-8')
        cls.navigation_source = (Path(__file__).resolve().parent / 'qt_navigation_builder.py').read_text(encoding='utf-8')

    def test_read_only_entry_point_and_no_save_mutation(self):
        self.assertIn('SaveDocument.load(', self.source)
        self.assertNotIn('produce(', self.source)
        self.assertIn('self.session.save_as(', self.source)  # Phase 2B safe producer
        self.assertIn('NoEditTriggers', self.source)

    def test_map_editor_entry_point_is_honest(self):
        self.assertIn("QPushButton('Open Map Editor')", self.source)
        self.assertIn('self.map_button.setEnabled(False)', self.source)
        self.assertIn('available in the Tkinter application', self.source)

    def test_load_batches_navigation_and_supports_diagnostics(self):
        self.assertIn('self.navigation.setUpdatesEnabled(False)', self.navigation_source)
        self.assertIn('self.navigation.setUpdatesEnabled(True)', self.navigation_source)
        self.assertIn('FREECOL_QT_PROFILE', self.source)
        self.assertIn('self.navigation_icons.icon(kind, nation_id, native)', self.navigation_source)
        self.assertNotIn('standardIcon(', self.source)

    def test_navigation_styles_preserve_semantic_filters(self):
        self.assertIn("self.navigation.setIndentation(19)", self.source)
        self.assertIn("kind='nation'", self.navigation_source)
        self.assertIn("kind='colony'", self.navigation_source)
        self.assertIn("item.setData(0, Qt.ItemDataRole.UserRole, (group, scope))", self.navigation_source)
        self.assertIn("item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)", self.navigation_source)

    def test_detail_unit_navigation_is_read_only(self):
        self.assertIn("self.jump_unit_button.clicked.connect(self.open_detail_unit)", self.source)
        self.assertIn("self.document.unit_by_id(unit_id)", self.source)
        self.assertIn("select_record_in_view(self.model_view, self.record_model, unit)", self.source)
        self.assertNotIn('self.document.save(', self.source)

    def test_global_search_sort_preserves_record_identity(self):
        self.assertIn('results.setSortingEnabled(True)', self.global_search_source)
        self.assertIn('results.setSortingEnabled(False)', self.global_search_source)
        self.assertIn('cell.setData(Qt.ItemDataRole.UserRole, row)', self.global_search_source)
        self.assertIn('matches[source_index]', self.global_search_source)

    def test_colony_row_minis_use_approved_art_resolver(self):
        self.assertIn('resolve_colony_graphic(record)', self.source)
        self.assertIn('if self.group == \'Colonies\':', self.source)
        self.assertIn('Qt.TransformationMode.SmoothTransformation', self.source)

    def test_workspace_rows_keep_identity_with_icons(self):
        self.assertIn("if col == 0 and self.group != 'Founding Fathers':", self.source)
        self.assertIn("model_decorations[(row, col)] = icon", self.source)
        self.assertIn("self.record_model.set_presentation(model_decorations, model_tooltips)", self.source)
        self.assertIn("self.model_view = build_record_table_view", self.source)

    def test_final_unit_rows_and_navigation_cleanup(self):
        self.assertIn("apply_record_view_sizing(self.model_view, self.group)", self.source)
        self.assertNotIn("entry(my, 'Research'", self.navigation_source)
        self.assertNotIn("entry(rival, 'Research'", self.navigation_source)
        self.assertIn("entry(None, 'Map', ready=False, kind='map')", self.navigation_source)

    def test_full_units_list_offers_actual_raw_xml_navigation(self):
        self.assertIn("self.unit_xml_button = QPushButton('View selected unit XML →')", self.source)
        self.assertIn("self.unit_xml_button.setVisible(self.group == 'Units')", self.source)
        self.assertIn("self.inspector_tabs.setCurrentWidget(self.raw_xml)", self.source)
        self.assertIn("self.unit_xml_button.hide()", self.source)

    def test_unit_drilldown_visibility_tracks_real_unit_selection(self):
        self.assertIn("self.jump_unit_button.setVisible(unit is not None)", self.detail_source)
        self.assertIn("self.jump_unit_button.hide()", self.source)
        self.assertIn("self.document.unit_by_id(unit_id)", self.source)

    def test_colony_goods_action_only_visible_in_breakdown_context(self):
        self.assertIn("self.jump_colony_button.setVisible(relevant)", self.detail_source)
        self.assertIn("self.tabs.currentWidget() is table", self.detail_source)
        self.assertIn("self.group == 'National Goods'", self.source)
        self.assertIn("self.refresh_breakdown_action(self.tabs.currentIndex())", self.source)

    def test_vertical_workspace_splitter(self):
        self.assertIn('self.workspace_splitter = QSplitter(Qt.Orientation.Vertical)', self.source)
        self.assertIn('self.workspace_splitter.addWidget(self.workspace_table_area)', self.source)
        self.assertIn('self.workspace_splitter.addWidget(self.tabs)', self.source)
        self.assertIn('self.workspace_splitter.setChildrenCollapsible(False)', self.source)

    def test_separate_workspace_and_inspector(self):
        self.assertIn('self.overview = OverviewPanel()', self.source)
        self.assertIn('self.details = InspectorDetails()', self.source)
        self.assertIn('self.raw_xml = QPlainTextEdit()', self.source)
        self.assertIn('self.model_view.selectionModel().currentChanged.connect(', self.source)


if __name__ == '__main__':
    unittest.main()
