"""Run the headless suite and explicitly dispose Qt objects before interpreter exit.

Unlike a forced os._exit(), this retains Python's ordinary shutdown path so
segmentation faults continue to make CI fail.
"""
import gc
import sys
import unittest


def cleanup_qt():
    """Close live test windows while QApplication and Qt are still functional."""
    from PySide6.QtCore import QCoreApplication, QEvent
    from PySide6.QtWidgets import QApplication
    from shiboken6 import delete, isValid

    app = QApplication.instance()
    if app is None:
        return

    # Tests may keep Python references to their windows after the test ends.
    # Destroy the underlying C++ widgets while Qt is still operational;
    # shiboken then invalidates the Python wrappers safely.
    windows = list(app.topLevelWidgets())
    for widget in windows:
        if isValid(widget):
            widget.close()
    app.processEvents()
    for widget in windows:
        if isValid(widget):
            delete(widget)
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()
    gc.collect()
    remaining = [widget for widget in app.topLevelWidgets() if isValid(widget)]
    if remaining:
        raise RuntimeError(f'Qt test teardown left {len(remaining)} top-level widgets')


def main():
    suite = unittest.defaultTestLoader.discover('.', pattern='test_*.py')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    try:
        cleanup_qt()
    except Exception as exc:
        print(f'Qt cleanup failed: {exc}', file=sys.stderr)
        return 1
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
