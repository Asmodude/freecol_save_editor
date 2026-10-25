"""Portable savegame folder discovery shared by UI frontends."""
from pathlib import Path


def save_directory(home=None, previous=None):
    """Prefer an existing last-used directory, then conventional FreeCol saves."""
    home = Path(home) if home is not None else Path.home()
    if previous:
        folder = Path(previous).expanduser()
        if folder.is_dir():
            return folder
    for base in (home / 'Documents', home / 'Dokumenter',
                 home / 'OneDrive' / 'Documents', home / 'OneDrive' / 'Dokumenter'):
        for name in ('freecol', 'FreeCol'):
            folder = base / name / 'save'
            if folder.is_dir():
                return folder
    return home
