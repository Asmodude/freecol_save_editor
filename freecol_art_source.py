"""UI-free discovery and byte reading for artwork in the local FreeCol installation.

This module deliberately does not import tkinter, Pillow or other UI libraries.
"""
from pathlib import Path
import zipfile

_custom_root = None


def set_installation_root(path):
    """Override artwork discovery for this process; None restores automatic discovery."""
    global _custom_root
    _custom_root = Path(path).expanduser() if path else None


def configured_root():
    return _custom_root


def installation_roots():
    return [
        Path(r'C:\Program Files\FreeCol'),
        Path(r'C:\Program Files (x86)\FreeCol'),
        Path(r'C:\Programmer\FreeCol'),
        Path.home() / 'FreeCol',
        Path.home() / 'OneDrive' / 'Dokumenter' / 'freecol',
        Path.home() / 'OneDrive' / 'Documents' / 'freecol',
        Path.home() / 'Documents' / 'FreeCol',
        Path.cwd(),
    ]


def discover(roots=None):
    """Return (base, archive, prefix, status) using the accepted search order."""
    if roots is None:
        roots = [_custom_root] if _custom_root is not None else installation_roots()
    possible=[
        'app/data/default/resources/images',
        'data/default/resources/images',
        'default/resources/images',
        'resources/images',
        'data/base/resources/images',
    ]
    for root in roots:
        root=Path(root)
        for rel in ('', *possible):
            img=root / rel
            if (img / 'terrain').is_dir() or (img / 'units').is_dir() or (img / 'goods').is_dir():
                return img,None,'',f'FreeCol graphics: {img} (preview uses local textures with simple overlays)'
        if not root.is_dir():
            continue
        for arc in list(root.glob('*.jar'))+list(root.glob('*.zip')):
            try:
                with zipfile.ZipFile(arc) as zf:
                    names=zf.namelist()
                    match=next((n for n in names if n.endswith('terrain/savannah/center0.size9.png')),None)
                    if not match:
                        match=next((n for n in names if n.endswith('terrain/savannah/center0.png')),None)
                if not match:
                    match = next((n for n in names if '/units/' in n and n.endswith('.png')), None)
                if not match:
                    match = next((n for n in names if '/goods/' in n and n.endswith('.png')), None)
                if match and '/units/' in match:
                    return None,arc,match.split('units/')[0],f'FreeCol graphics archive: {arc.name}'
                if match and '/goods/' in match:
                    return None,arc,match.split('goods/')[0],f'FreeCol graphics archive: {arc.name}'
                if match:
                    suffix=('terrain/savannah/center0.size9.png' if match.endswith('center0.size9.png')
                            else 'terrain/savannah/center0.png')
                    return None,arc,match[:-len(suffix)],f'FreeCol graphics archive: {arc.name} (preview uses local textures with simple overlays)'
            except (OSError,zipfile.BadZipFile):
                pass
    return None,None,'','FreeCol graphics not found — terrain labels shown instead.'


def read_bytes(base,archive,prefix,relpath):
    """Read installed artwork without loading any toolkit image objects."""
    if base:
        fp=Path(base)/relpath
        if fp.is_file():
            return fp.read_bytes()
    if archive:
        try:
            with zipfile.ZipFile(archive) as zf:
                return zf.read(prefix+relpath)
        except (OSError,KeyError,zipfile.BadZipFile):
            return None
    return None


def validate_installation(path):
    """Accept only folders with real FreeCol artwork, not arbitrary directories."""
    root = Path(path).expanduser()
    if not root.is_dir():
        return False, 'The selected folder does not exist.'
    base, archive, prefix, status = discover([root])
    if base is None and archive is None:
        return False, 'No FreeCol artwork directory or resource archive was found.'
    return True, status
