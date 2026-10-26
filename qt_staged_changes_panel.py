"""Review and undo controls for staged FreeCol edits.

The panel never mutates XML. All edits belong to EditSession, and the caller
is responsible for refreshing the affected views after a change is unstaged.
"""
from PySide6.QtCore import Signal, Qt
import presentation
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget, QMessageBox,
)


class StagedChangesPanel(QWidget):
    """An explicit review surface; keys retain their original Python types."""

    changed = Signal()

    def __init__(self, session, parent=None, document=None):
        super().__init__(parent)
        self.session = session
        self.document = document
        layout = QVBoxLayout(self)
        self.heading = QLabel()
        layout.addWidget(self.heading)
        self.tree = QTreeWidget()
        self.tree.setColumnCount(5)
        self.tree.setHeaderLabels(("Record", "Field", "Original", "Staged", ""))
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
        self.refresh()

    def labels_for(self, key, original, staged):
        record_id, field = key
        lookup_id = record_id.split('|', 1)[0]
        element = None
        doc = self.document
        if doc is not None:
            element = doc.players.get(lookup_id)
            if element is None:
                element = next((e for e in doc.colonies + doc.native_settlements + doc.units
                                if e.get('id') == lookup_id), None)
        name = (element.get('name') or element.get('username') or lookup_id) if element is not None else lookup_id
        kind = ('player' if lookup_id.startswith('player:') else
                'colony' if lookup_id.startswith('colony:') else
                'native settlement' if lookup_id.startswith('indianSettlement:') else 'unit')
        if element is not None and element.get('owner') and doc is not None:
            name += ' — ' + doc.owner_name(element.get('owner'))
        title = f'{name} ({kind})'
        if field.startswith(('delete',)):
            label = 'Delete ' + kind
            return title, label, 'Present', 'Delete'
        if field == 'equipment':
            def role(value):
                return f'{presentation.readable(value[0])} × {value[1]}'
            return title, 'Equipment', role(original), role(staged)
        if field.startswith(('stance|', 'tension|', 'alarm|')):
            topic, other = field.split('|', 1)
            counterpart = doc.owner_name(other) if doc is not None else other
            label = presentation.readable(topic) + ' — ' + counterpart
        elif field == 'sonsOfLibertyTarget':
            label = 'Sons of Liberty'
        else:
            label = presentation.readable(field)
        return title, label, str(original), str(staged)

    def refresh(self):
        self.tree.clear()
        for key, (original, staged) in self.session.items():
            item = QTreeWidgetItem(self.labels_for(key, original, staged))
            item.setData(0, Qt.ItemDataRole.UserRole, key)
            item.setToolTip(0, str(key))
            self.tree.addTopLevelItem(item)
            undo = QPushButton('↶')
            undo.setObjectName('undoStagedChange')
            undo.setToolTip('Undo this change (restore opened-save value)')
            undo.setFixedWidth(28)
            undo.clicked.connect(lambda checked=False, edit_key=key: self.undo_key(edit_key))
            self.tree.setItemWidget(item, 4, undo)
        self.tree.setColumnWidth(0, 110)
        self.tree.setColumnWidth(1, 75)
        self.tree.setColumnWidth(2, 60)
        self.tree.setColumnWidth(3, 60)
        self.tree.setColumnWidth(4, 33)
        count = self.session.count
        self.heading.setText(f"Pending changes: {count}")
        self.clear_button.setEnabled(count > 0)
        self._update_buttons()

    def _update_buttons(self):
        self.undo_button.setEnabled(bool(self.tree.selectedItems()))

    def undo_selected(self):
        selection = self.tree.selectedItems()
        if not selection:
            return
        key = selection[0].data(0, Qt.ItemDataRole.UserRole)
        if key not in self.session.edits:
            return
        self.undo_key(key)

    def undo_key(self, key):
        if key not in self.session.edits:
            return
        if self.document is not None and hasattr(self.document, 'xml_bytes'):
            from edit_preflight import unstage_checked
            try:
                unstage_checked(self.session, self.document.xml_bytes, key)
            except ValueError as exc:
                QMessageBox.warning(self, 'Cannot undo staged change', str(exc))
                return
        else:
            self.session.unstage(key)
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
