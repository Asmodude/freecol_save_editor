"""Record-aware sorting proxy for read-only Qt model/view migration.

Match the accepted QTableWidget numeric-column semantics while preserving
the regular proxy's multi-column filtering and stable source record identity.
"""
from PySide6.QtCore import QSortFilterProxyModel, Qt
from qt_sorting import NUMERIC_COLUMNS, sort_key
from qt_final_visual_format import established_turn
from qt_property_display import compact_property_value


class RecordSortFilterProxy(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._record_group = None

    def set_record_group(self, group):
        self._record_group = group
        self.invalidate()

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        value = super().data(index, role)
        if role != Qt.ItemDataRole.DisplayRole or not index.isValid():
            return value
        heading = self.headerData(index.column(), Qt.Orientation.Horizontal)
        if self._record_group == 'Colonies' and heading == 'Established':
            return established_turn(value)
        if self._record_group == 'Game properties' and heading == 'Saved value':
            return compact_property_value(value)
        return value

    def lessThan(self, left, right):
        source = self.sourceModel()
        heading = source.headerData(left.column(), Qt.Orientation.Horizontal)
        numeric = heading in NUMERIC_COLUMNS.get(self._record_group, ())
        left_value = source.data(left, Qt.ItemDataRole.DisplayRole)
        right_value = source.data(right, Qt.ItemDataRole.DisplayRole)
        return sort_key(left_value, numeric) < sort_key(right_value, numeric)
