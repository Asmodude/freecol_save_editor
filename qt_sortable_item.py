"""Reusable numeric-aware, stable QTableWidget item for legacy Qt tables."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem
from qt_sorting import sort_key


class SortableItem(QTableWidgetItem):
    """Keep row identity and source sort values when a widget paints the cell."""
    SourceSortRole = Qt.ItemDataRole.UserRole + 2
    def __init__(self, value, numeric=False):
        super().__init__('' if value is None else str(value))
        self.numeric = numeric
        if numeric:
            self.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    def __lt__(self, other):
        left = self.data(self.SourceSortRole)
        right = other.data(self.SourceSortRole)
        return sort_key(self.text() if left is None else left, self.numeric) < sort_key(
            other.text() if right is None else right, self.numeric)


