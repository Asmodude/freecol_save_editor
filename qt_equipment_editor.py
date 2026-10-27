"""Shared PySide6 equipment editor. FreeCol rules stay in the backend."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from equipment_rules import ROLES, validate_equipment
from presentation import equipment_description, ROLE_LABELS
from qt_equipment_controls import WheelSafeComboBox, WheelSafeSpinBox
from qt_stage_controls import StageChangeButton, style_stage_choice

_LEGACY_ROLE_LABELS = {
    'model.role.default': 'Unequipped colonist',
    'model.role.soldier': 'Soldier (50 muskets)',
    'model.role.dragoon': 'Dragoon (50 muskets, 50 horses)',
    'model.role.scout': 'Scout (50 horses)',
    'model.role.pioneer': 'Pioneer (tools)',
}

class EquipmentEditor(QWidget):
    """One set of controls for Overview and Stationed units; no staging logic."""
    stage_requested = Signal(str, str, int)

    def __init__(self, document, unit, session, *, context='overview', parent=None):
        super().__init__(parent)
        uid = unit.get('id')
        original_role = unit.get('role', 'model.role.default')
        original_count = int(unit.get('roleCount', '0' if original_role == 'model.role.default' else '1'))
        planned = session.staged_value((uid, 'equipment'), (original_role, original_count))
        pending = session.is_changed((uid, 'equipment'))
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0 if context == 'overview' else 2, 0 if context == 'overview' else 1,
                                  0 if context == 'overview' else 2, 0 if context == 'overview' else 1)
        layout.setSpacing(3)
        self.selector = WheelSafeComboBox(self)
        self.selector.setObjectName('unitEquipmentRole' if context == 'overview' else 'stationedEquipmentRole')
        self.selector.setProperty('unitId', uid)
        style_stage_choice(self.selector, pending)
        rules = getattr(document, 'equipment_rules_index', None)
        for role in ROLES:
            try:
                validate_equipment(document.root, unit, role,
                                   0 if role == 'model.role.default' else 1, rules=rules)
            except (ValueError, TypeError):
                continue
            self.selector.addItem(ROLE_LABELS.get(role, role.rsplit('.', 1)[-1].title()), role)
        self.count = WheelSafeSpinBox(self)
        self.count.setObjectName('unitEquipmentCount' if context == 'overview' else 'stationedEquipmentTools')
        self.tools_label = QLabel('', self)
        self.tools_label.setObjectName('pioneerToolQuantity')
        self.status = QLabel(self)
        self.status.setObjectName('unitEquipmentStatus' if context == 'overview' else 'stationedEquipmentStatus')
        self.button = StageChangeButton(self)
        self.button.setObjectName('stageUnitEquipment' if context == 'overview' else 'stageStationedEquipment')
        self.button.setToolTip('Stage unit equipment; no warehouse stock is consumed')
        self.button.clicked.connect(lambda _checked=False: self.stage_requested.emit(uid, self.selector.currentData(), self.count.value()))
        layout.addWidget(self.selector, 2)
        layout.addWidget(self.count, 1)
        layout.addWidget(self.tools_label)
        layout.addWidget(self.status)
        layout.addWidget(self.button)
        limits = ({key: int(elements[0].get('maximum-count', '1'))
                   for key, elements in rules.roles.items() if len(elements) == 1}
                  if rules is not None else
                  {e.get('id'): int(e.get('maximum-count', '1')) for e in document.root.iter('role')})

        def update_role(_index):
            role = self.selector.currentData()
            limit = max(1, limits.get(role, 1))
            if role == 'model.role.default':
                self.count.setRange(0, 0)
            else:
                self.count.setRange(1, limit)
            if role == 'model.role.pioneer':
                self.count.setValue(min(5, limit))
            self.count.setVisible(role == 'model.role.pioneer')
            self.count.setEnabled(role == 'model.role.pioneer' and limit > 1)
            self.count.setSuffix(' × 20 tools' if role == 'model.role.pioneer' else '')
            self.count.setToolTip('Pioneer: 1–5 means 20–100 tools' if role == 'model.role.pioneer'
                                  else 'Equipment count defined by the save ruleset')
            update_display()

        def update_display(*_args):
            role = self.selector.currentData()
            choice = (role, self.count.value())
            self.tools_label.setText({
                'model.role.default': 'No equipment',
                'model.role.soldier': '50 muskets',
                'model.role.dragoon': '50 muskets + 50 horses',
                'model.role.scout': '50 horses',
                'model.role.pioneer': f'{self.count.value() * 20} tools',
            }.get(role, ''))
            if choice != planned:
                self.status.setText('Not staged')
                self.status.setToolTip('Original: ' + equipment_description(original_role, original_count) + '; staged: ' + equipment_description(*planned) +
                                       '; current selection not staged')
            elif pending:
                self.status.setText('Staged')
                self.status.setToolTip('Original: ' + equipment_description(original_role, original_count) + '; staged: ' + equipment_description(*planned))
            else:
                self.status.setText('')
                self.status.setToolTip('Original: ' + equipment_description(original_role, original_count))
            self.button.setEnabled(role is not None)

        self.selector.currentIndexChanged.connect(update_role)
        self.count.valueChanged.connect(update_display)
        selected = self.selector.findData(planned[0])
        if (not pending and original_role == 'model.role.default'
                and 'hardypioneer' in (unit.get('unitType') or '').lower()):
            pioneer = self.selector.findData('model.role.pioneer')
            if pioneer >= 0:
                selected = pioneer
        if self.selector.count() == 1 and self.selector.itemData(0) == 'model.role.default':
            # A non-personnel unit has no equipment choices; do not invite a
            # meaningless Default -> Default staging action.
            self.selector.setEnabled(False)
            self.button.setEnabled(False)
            self.selector.setToolTip('No alternative equipment roles are valid for this unit')
        if selected >= 0:
            self.selector.setCurrentIndex(selected)
            update_role(selected)
            self.count.setValue(planned[1] if planned[0] == self.selector.currentData()
                                else min(5, self.count.maximum()) if self.selector.currentData() == 'model.role.pioneer'
                                else 1)
        else:
            self.selector.setEnabled(False)
            self.count.setEnabled(False)
            self.selector.setToolTip('No eligible roles can be verified from the saved ruleset')
            self.button.setEnabled(False)
        update_display()
        if self.selector.count() == 1 and self.selector.itemData(0) == 'model.role.default':
            self.button.setEnabled(False)
