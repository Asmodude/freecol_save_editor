"""Regression tests for scroll-safe equipment editors."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication
from qt_equipment_controls import WheelSafeComboBox, WheelSafeSpinBox


class EquipmentWheelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_closed_combo_ignores_wheel_even_when_focused(self):
        control = WheelSafeComboBox()
        try:
            control.addItems(['Soldier', 'Dragoon', 'Scout'])
            control.setCurrentIndex(0)
            control.show()
            control.setFocus()
            wheel = QWheelEvent(QPointF(10, 10), QPointF(10, 10), QPoint(0, 0),
                                QPoint(0, -120), Qt.MouseButton.NoButton,
                                Qt.KeyboardModifier.NoModifier, Qt.ScrollPhase.ScrollUpdate, False)
            control.wheelEvent(wheel)
            self.assertEqual(control.currentIndex(), 0)
            self.assertFalse(wheel.isAccepted())
        finally:
            control.close()

    def test_tools_spinbox_ignores_wheel(self):
        control = WheelSafeSpinBox()
        try:
            control.setRange(1, 5)
            control.setValue(3)
            control.show()
            control.setFocus()
            wheel = QWheelEvent(QPointF(10, 10), QPointF(10, 10), QPoint(0, 0),
                                QPoint(0, 120), Qt.MouseButton.NoButton,
                                Qt.KeyboardModifier.NoModifier, Qt.ScrollPhase.ScrollUpdate, False)
            control.wheelEvent(wheel)
            self.assertEqual(control.value(), 3)
            self.assertFalse(wheel.isAccepted())
        finally:
            control.close()


if __name__ == '__main__':
    unittest.main()
