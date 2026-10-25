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


def apply_record_view_sizing(view, group):
    """Match Phase 1 icon dimensions and row heights in the new view."""
    from PySide6.QtCore import QSize
    sizes = {
        "Colonies": QSize(32, 30),
        "Founding Fathers": QSize(60, 65),
        "Native settlements": QSize(60, 20),
        "Units": QSize(42, 42),
    }
    view.setIconSize(sizes.get(group, QSize(20, 20)))
    height = 75 if group == "Founding Fathers" else 44 if group == "Units" else 36 if group == "Colonies" else None
    if height is not None:
        for row in range(view.model().rowCount()):
            view.setRowHeight(row, height)
    else:
        view.resizeRowsToContents()


def select_record_in_legacy_table(table, record_model, record):
    """Synchronise an old table by source object identity, not visual row."""
    if record is None:
        table.clearSelection()
        return False
    for visual_row in range(table.rowCount()):
        item = table.item(visual_row, 0)
        source_row = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        if isinstance(source_row, int) and record_model.record_at(source_row) is record:
            table.selectRow(visual_row)
            return True
    table.clearSelection()
    return False
