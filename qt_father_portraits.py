"""Find FreeCol's own Founding Father portraits without copying game artwork.

Scans expected resource directories and archives once per session, then returns
the exact image bytes. Missing artwork is a normal supported case.
"""
from pathlib import Path
from zipfile import ZipFile, BadZipFile
from freecol_art_source import installation_roots

IMAGE_EXTENSIONS={'.jpg','.jpeg','.png'}

def portrait_key(father_id):
    prefix='model.foundingFather.'
    if not isinstance(father_id,str) or not father_id.startswith(prefix):
        return None
    name=father_id[len(prefix):]
    return name if name and all(c.isascii() and (c.isalnum() or c=='_') for c in name) else None

class FatherPortraits:
    def __init__(self,roots=None):
        self.roots=list(installation_roots() if roots is None else roots)
        self.index=None
        self.cache={}

    def _scan(self):
        index={}
        for root in self.roots:
            root=Path(root)
            if not root.is_dir():
                continue
            for base in (root/'app/data/default/resources/images',
                         root/'data/default/resources/images',
                         root/'default/resources/images',
                         root/'resources/images'):
                folder=base/'foundingFathers'
                if folder.is_dir():
                    for file in folder.iterdir():
                        if file.suffix.lower() in IMAGE_EXTENSIONS:
                            index.setdefault(file.stem,(str(file),None))
            for archive in (*root.glob('*.jar'),*root.glob('*.zip')):
                try:
                    with ZipFile(archive) as z:
                        for name in z.namelist():
                            p=Path(name)
                            if p.parent.name=='foundingFathers' and p.suffix.lower() in IMAGE_EXTENSIONS:
                                index.setdefault(p.stem,(str(archive),name))
                except (OSError,BadZipFile):
                    continue
        self.index=index

    def get(self,father_id):
        key=portrait_key(father_id)
        if key is None:
            return None
        if key in self.cache:
            return self.cache[key]
        if self.index is None:
            self._scan()
        result=None
        for stem in (key, key+'.size6',key+'.size3'):
            source=self.index.get(stem)
            if source is None:
                continue
            filepath,member=source
            try:
                if member is None:
                    result=Path(filepath).read_bytes()
                else:
                    with ZipFile(filepath) as z:
                        result=z.read(member)
                break
            except (OSError,KeyError,BadZipFile):
                continue
        self.cache[key]=result
        return result
