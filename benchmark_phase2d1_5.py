"""Measure equipment editor construction on an actual FreeCol .fsg save.

Usage (Windows PowerShell):
    py benchmark_phase2d1_5.py "C:\\Users\\<you>\\Documents\\freecol\\save\\your-save.fsg"

Prints paired baseline/current results; this is a diagnostic, NOT a timing gate.
"""
import argparse
import os
import statistics
import time
from types import SimpleNamespace

from PySide6.QtWidgets import QApplication
from edit_session import EditSession
from qt_equipment_editor import EquipmentEditor
from save_document import SaveDocument


def sample_units(document, count):
    candidates = [unit for unit in document.units
                  if unit.get('owner') in document.players and unit.get('unitType')]
    if not candidates:
        raise ValueError('Save contains no eligible units for benchmark')
    return (candidates * (count // len(candidates) + 1))[:count]


def time_editors(document, units, repeats=3):
    durations = []
    for _ in range(repeats):
        editors = []
        started = time.perf_counter()
        for unit in units:
            editor = EquipmentEditor(document, unit, EditSession())
            editors.append(editor)
        durations.append((time.perf_counter() - started) * 1000)
        for editor in editors:
            editor.deleteLater()
    return statistics.median(durations)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('save', help='Path to a representative .fsg archive')
    parser.add_argument('--units', type=int, default=15)
    args = parser.parse_args()
    if args.units <= 0:
        parser.error('--units must be positive')
    QApplication.instance() or QApplication([])
    started = time.perf_counter()
    document = SaveDocument.load(args.save)
    load_ms = 1000 * (time.perf_counter() - started)
    units = sample_units(document, args.units)
    plain = SimpleNamespace(root=document.root)
    old_ms = time_editors(plain, units)
    new_ms = time_editors(document, units)
    print(f'Save: {args.save}; bytes: {len(document.xml_bytes):,}')
    print(f'Load + one-time index: {load_ms:.1f} ms')
    print(f'Uncached {len(units)} editors, median of 3: {old_ms:.1f} ms')
    print(f'Indexed  {len(units)} editors, median of 3: {new_ms:.1f} ms')
    print(f'Improvement: {(old_ms / new_ms):.2f}x' if new_ms else 'Invalid duration')


if __name__ == '__main__':
    main()
