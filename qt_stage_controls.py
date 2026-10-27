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

def style_stage_choice(combo, staged=False):
    """Apply the existing blue/editable and green/staged convention to Qt choices."""
    border = '#26815A' if staged else '#76A9E8'
    background = '#E5F5E9' if staged else '#EDF5FF'
    combo.setStyleSheet(
        'QComboBox { border: 2px solid ' + border +
        '; border-radius: 3px; padding: 2px; background: ' +
        background + '; color: #172B45; }'
    )
