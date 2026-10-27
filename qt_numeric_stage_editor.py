"""Reusable Qt numeric edit surface; staging and validation belong to the caller."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit
from qt_stage_controls import StageChangeButton


class NumericStageEditor(QWidget):
    """Keeps source value and pending text distinct; emits only on explicit stage."""
    stage_requested = Signal(str)

    def __init__(self, value, original, *, staged=False, object_name='numericInput',
                 button_name='stageNumeric', tooltip='', label_tooltip='Value in opened save',
                 margins=(2, 1, 2, 1), spacing=3, parent=None):
        super().__init__(parent)
        self._committed = str(value)
        line = QHBoxLayout(self)
        line.setContentsMargins(*margins)
        line.setSpacing(spacing)
        self.original_label = None
        if staged:
            self.original_label = QLabel('was ' + str(original), self)
            self.original_label.setObjectName(object_name + 'Original')
            self.original_label.setToolTip(label_tooltip)
            line.addWidget(self.original_label)
        self.edit = QLineEdit(self._committed, self)
        self.edit.setObjectName(object_name)
        self.edit.setToolTip(tooltip)
        self.edit.setStyleSheet(
            'QLineEdit { border: 2px solid ' + ('#26815A' if staged else '#76A9E8') +
            '; border-radius: 3px; padding: 2px; background: ' +
            ('#E5F5E9' if staged else '#EDF5FF') + '; color: #172B45; }')
        self.button = StageChangeButton(self)
        self.button.setObjectName(button_name)
        self.button.setToolTip('Stage this value (or press Enter)')
        self.edit.returnPressed.connect(self._request_stage)
        self.button.clicked.connect(lambda _checked=False: self._request_stage())
        line.addWidget(self.edit, 1)
        line.addWidget(self.button)

    def _request_stage(self):
        self.stage_requested.emit(self.edit.text())
