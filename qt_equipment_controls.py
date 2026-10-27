"""Equipment controls that don't steal table scrolling when unfocused."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QSpinBox


class WheelSafeComboBox(QComboBox):
    def wheelEvent(self, event):
        if self.view().isVisible():
            super().wheelEvent(event)
        else:
            event.ignore()


class WheelSafeSpinBox(QSpinBox):
    def wheelEvent(self, event):
        event.ignore()
