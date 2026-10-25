"""Founding Father portrait and inspection behaviour for the Qt explorer."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from qt_overview import record_overview
from qt_founding_fathers import father_source_node
from qt_raw_xml import formatted_record_xml


class FoundingFathersViewMixin:
    def _set_father_portrait(self, label, father_id, width, height):
        data = self.father_portraits.get(father_id)
        pixmap = QPixmap()
        if data and pixmap.loadFromData(data):
            label.setPixmap(pixmap.scaled(width, height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
        else:
            label.clear()
            label.setText('Portrait unavailable')

    def inspect_recruiting_father(self):
        if self.recruiting_father is not None:
            self.grid.clearSelection()
            self.inspect_father_record(self.recruiting_father)

    def inspect_father_record(self, element):
        self.selected_element = element
        self.update_detail_tabs(element)
        self.inspector_label.setText(element.get('name', 'Founding Father'))
        self.details.setPlainText(
            'Name: ' + element.get('name', '') + '\n' +
            'Category: Founding Fathers\n' +
            'Status: ' + element.get('status', '') + '\n' +
            'FreeCol identifier: ' + element.get('id', ''))
        self.overview.setPlainText(record_overview('Founding Fathers', element, self.document))
        source = father_source_node(self.document, element)
        self.raw_xml.setPlainText(
            formatted_record_xml(source) if source is not None else
            'No matching source XML node found for this Founding Father.')

