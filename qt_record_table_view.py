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
    view.setWordWrap(False)
    view.setShowGrid(True)
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


def select_record_in_view(view, record_model, record):
    """Select by XML object identity, never by a sorted display-row number."""
    if record is None:
        view.clearSelection()
        return False
    proxy = view.model()
    for source_row in range(record_model.rowCount()):
        if record_model.record_at(source_row) is record:
            mapped = proxy.mapFromSource(record_model.index(source_row, 0))
            if not mapped.isValid():
                view.clearSelection()
                return False
            view.setCurrentIndex(mapped)
            view.selectRow(mapped.row())
            return True
    view.clearSelection()
    return False
