"""Workspace heading and nation-emblem presentation for Qt views."""
from PySide6.QtGui import QPixmap
from qt_workspace_header import workspace_identity
from qt_flag_icons import flag_pixmap


class WorkspaceHeaderMixin:
    def update_workspace_header(self):
        title, subtitle, nation_id, native, placeholder = workspace_identity(
            self.document, self.group, self.scope)
        self.workspace_title.setText(title)
        self.workspace_subtitle.setText(subtitle)
        self.search.setPlaceholderText(placeholder)
        emblem = self.navigation_icons.icon(
            'nation' if nation_id else 'map' if self.group == 'Game properties' else 'section',
            nation_id=nation_id, native=native, size=48)
        flag = flag_pixmap(nation_id, 39) if nation_id and not native else QPixmap()
        self.workspace_emblem.setPixmap(flag if not flag.isNull() else emblem.pixmap(48, 48))

