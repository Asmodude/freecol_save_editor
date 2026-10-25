"""About dialog: product version follows ROADMAP.md; Qt is a preview."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFrame, QHBoxLayout, QLabel, QVBoxLayout

APP_VERSION = '0.6.2.6.4'
BUILD_DATE = '25 October 2026'
PROJECT_OWNER = 'Morten Olsson'


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('About FreeCol Save Editor')
        self.setMinimumWidth(490)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(12)

        name = QLabel('FreeCol Save Editor')
        font = QFont(name.font())
        font.setPointSize(max(16, font.pointSize() + 5))
        font.setBold(True)
        name.setFont(font)
        layout.addWidget(name)

        edition = QLabel('Version ' + APP_VERSION + '  ·  Qt Preview (READ ONLY)')
        edition.setStyleSheet('color: palette(mid);')
        layout.addWidget(edition)

        rule = QFrame()
        rule.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(rule)

        description = QLabel(
            'A graphical explorer for FreeCol savegames. '
            'The Qt preview never saves or modifies game files.')
        description.setWordWrap(True)
        layout.addWidget(description)

        credit = QLabel('Developed by ' + PROJECT_OWNER + '\nBuild date: ' + BUILD_DATE)
        credit.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(credit)

        artwork = QLabel(
            'Game artwork is loaded from your FreeCol installation; '
            'no FreeCol artwork is bundled. Map editing and save editing '
            'remain available in the original Tkinter application.')
        artwork.setWordWrap(True)
        artwork.setStyleSheet('color: palette(mid);')
        layout.addWidget(artwork)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
