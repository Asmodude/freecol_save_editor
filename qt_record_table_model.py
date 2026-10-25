"""Read-only Qt record table model, preparatory infrastructure for Phase 2A.

The initial model deliberately does not replace the accepted QTableWidget UI.
It preserves source-record identity independently of sorting/filtering and
does not mutate records. Wiring it into views requires separate parity tests.
"""
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QIcon


class RecordTableModel(QAbstractTableModel):
    RecordRole = Qt.ItemDataRole.UserRole + 1

    def __init__(self, headings=(), rows=(), parent=None):
        super().__init__(parent)
        self._headings = tuple(headings)
        self._rows = tuple(rows)
        self._decorations = {}
        self._tooltips = {}

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._headings)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headings[section] if 0 <= section < len(self._headings) else None
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        record, values = self._rows[index.row()]
        if role == self.RecordRole:
            return record
        if role == Qt.ItemDataRole.DecorationRole:
            return self._decorations.get((index.row(), index.column()))
        if role == Qt.ItemDataRole.ToolTipRole:
            return self._tooltips.get((index.row(), index.column()))
        if role == Qt.ItemDataRole.DisplayRole and 0 <= index.column() < len(values):
            value = values[index.column()]
            return '' if value is None else str(value)
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def record_at(self, row):
        """Return the authoritative source record or None for an invalid row."""
        return self._rows[row][0] if 0 <= row < len(self._rows) else None

    def set_presentation(self, decorations=None, tooltips=None):
        """Set view-only metadata keyed by original model row and column."""
        self._decorations = dict(decorations or {})
        self._tooltips = dict(tooltips or {})
        if self.rowCount() and self.columnCount():
            self.dataChanged.emit(self.index(0, 0),
                                  self.index(self.rowCount()-1, self.columnCount()-1),
                                  [Qt.ItemDataRole.DecorationRole, Qt.ItemDataRole.ToolTipRole])

    def replace_rows(self, rows, headings=None):
        self.beginResetModel()
        if headings is not None:
            self._headings = tuple(headings)
        self._rows = tuple(rows)
        self._decorations.clear()
        self._tooltips.clear()
        self.endResetModel()
