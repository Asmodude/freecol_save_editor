"""UI-free discovery and byte reading for artwork in the local FreeCol installation.

This module deliberately does not import tkinter, Pillow or other UI libraries.
"""
from pathlib import Path
import zipfile


def installation_roots():
    return [
        Path(r'C:\Program Files\FreeCol'),
        Path(r'C:\Program Files (x86)\FreeCol'),
        Path(r'C:\Programmer\FreeCol'),
        Path.home() / 'FreeCol',
        Path.cwd(),
    ]


def discover(roots=None):
    """Return (base, archive, prefix, status) using the accepted search order."""
    if roots is None:
        roots=installation_roots()
    possible=[
        'app/data/default/resources/images',
        'data/default/resources/images',
        'default/resources/images',
        'resources/images',
        'data/base/resources/images',
    ]
    for root in roots:
        root=Path(root)
        for rel in possible:
            img=root / rel
            if (img / 'terrain').is_dir():
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
