"""Reusable numeric-aware, stable QTableWidget item for legacy Qt tables."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem
from qt_sorting import sort_key


class SortableItem(QTableWidgetItem):
    """Keep row identity attached to items during Qt sorting."""
    def __init__(self, value, numeric=False):
        super().__init__('' if value is None else str(value))
        self.numeric = numeric
        if numeric:
            self.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    def __lt__(self, other):
        return sort_key(self.text(), self.numeric) < sort_key(other.text(), self.numeric)


