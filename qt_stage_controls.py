"""Reusable PySide6 staging presentation control.

This widget intentionally owns *only* presentation, not FreeCol validation,
record identity, or the staging transaction.
"""
from PySide6.QtWidgets import QPushButton


class StageChangeButton(QPushButton):
    """Uniform, accessible explicit staging action across Qt editor views."""

    def __init__(self, parent=None):
        super().__init__("Stage Change", parent)
        self.setAccessibleName("Stage Change")
        self.setMinimumWidth(self.sizeHint().width())
        self.setToolTip("Stage this change; changes are not written until Save As")
