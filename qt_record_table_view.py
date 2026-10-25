"""QTableView-based read-only preview for the Phase 2A model migration.

The accepted QTableWidget remains the default visible table. This sibling
view proves Qt's model/proxy/delegate wiring without changing its behaviour.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableView, QAbstractItemView, QHeaderView


def build_record_table_view(proxy, parent=None):
    view = QTableView(parent)
    view.setModel(proxy)
    view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    view.setAlternatingRowColors(True)
    view.setSortingEnabled(True)
    view.verticalHeader().setVisible(False)
    view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    return view


def selected_source_record(view, record_model):
    """Resolve a proxy selection to the actual XML element, not the view row."""
    current = view.currentIndex()
    if not current.isValid():
        return None
    source = view.model().mapToSource(current)
    return record_model.record_at(source.row()) if source.isValid() else None
