"""Review and undo controls for staged FreeCol edits.

The panel never mutates XML. All edits belong to EditSession, and the caller
is responsible for refreshing the affected views after a change is unstaged.
"""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget, QMessageBox,
)


class StagedChangesPanel(QWidget):
    """An explicit review surface; keys retain their original Python types."""

    changed = Signal()

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        layout = QVBoxLayout(self)
        self.heading = QLabel()
        layout.addWidget(self.heading)
        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(("Record", "Field", "Original", "Staged"))
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.tree.itemSelectionChanged.connect(self._update_buttons)
        layout.addWidget(self.tree)
        buttons = QHBoxLayout()
        self.undo_button = QPushButton("Undo selected")
        self.undo_button.clicked.connect(self.undo_selected)
        self.clear_button = QPushButton("Unstage all")
        self.clear_button.clicked.connect(self.unstage_all)
        buttons.addWidget(self.undo_button)
        buttons.addWidget(self.clear_button)
        layout.addLayout(buttons)
        self._keys = []
        self.refresh()

    def refresh(self):
        """Render session state without changing or interpreting edit keys."""
        self.tree.clear()
        self._keys = []
        for key, (original, staged) in self.session.items():
            self._keys.append(key)
            label = (str(key[0]), str(key[1]), str(original), str(staged))
            self.tree.addTopLevelItem(QTreeWidgetItem(label))
        count = self.session.count
        self.heading.setText(f"Pending changes: {count}")
        self.clear_button.setEnabled(count > 0)
        self._update_buttons()

    def _update_buttons(self):
        self.undo_button.setEnabled(
            len(self.tree.selectedItems()) == 1 and self.tree.indexOfTopLevelItem(
                self.tree.selectedItems()[0]) < len(self._keys)
            if self.tree.selectedItems() else False
        )

    def undo_selected(self):
        selection = self.tree.selectedItems()
        if not selection:
            return
        index = self.tree.indexOfTopLevelItem(selection[0])
        if not 0 <= index < len(self._keys):
            return
        self.session.unstage(self._keys[index])
        self.refresh()
        self.changed.emit()

    def unstage_all(self):
        if not self.session.count:
            return
        choice = QMessageBox.question(
            self, 'Discard staged changes',
            f'Discard all {self.session.count} staged changes?',
            QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if choice != QMessageBox.StandardButton.Discard:
            return
        self.session.clear()
        self.refresh()
        self.changed.emit()
