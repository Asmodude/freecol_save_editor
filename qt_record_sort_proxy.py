"""Record-aware sorting proxy for read-only Qt model/view migration.

Match the accepted QTableWidget numeric-column semantics while preserving
the regular proxy's multi-column filtering and stable source record identity.
"""
from PySide6.QtCore import QSortFilterProxyModel, Qt
from qt_sorting import NUMERIC_COLUMNS, sort_key


class RecordSortFilterProxy(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._record_group = None

    def set_record_group(self, group):
        self._record_group = group
        self.invalidate()

    def lessThan(self, left, right):
        source = self.sourceModel()
        heading = source.headerData(left.column(), Qt.Orientation.Horizontal)
        numeric = heading in NUMERIC_COLUMNS.get(self._record_group, ())
        left_value = source.data(left, Qt.ItemDataRole.DisplayRole)
        right_value = source.data(right, Qt.ItemDataRole.DisplayRole)
        return sort_key(left_value, numeric) < sort_key(right_value, numeric)
