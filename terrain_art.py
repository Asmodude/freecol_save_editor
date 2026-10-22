"""FreeCol terrain artwork helper.

Loads artwork directly from a local FreeCol installation. No graphics are redistributed
inside the editor ZIP. The preview intentionally remains a viewer/editor aid rather than
an exact clone of FreeCol's Java renderer.
"""
from pathlib import Path
import tkinter as tk
import zipfile
import base64

TERRAIN_ALIASES = {
    'highSeas': 'highSeas',
    'lake': 'ocean',
    'greatRiver': 'river',
}
FOREST_KEYS = {
    'broadleafForest': 'broadleaf',
    'scrubForest': 'scrub',
    'coniferForest': 'conifer',
    'mixedForest': 'mixed',
    'tropicalForest': 'tropical',
    'rainForest': 'rain',
    'wetlandForest': 'wetland',
    'borealForest': 'boreal',
}
BONUS_KEYS = {
    'grain': 'grain', 'sugar': 'sugar', 'cotton': 'cotton', 'tobacco': 'tobacco',
    'lumber': 'lumber', 'furs': 'furs', 'ore': 'ore', 'silver': 'silver',
    'fish': 'fish', 'game': 'game', 'minerals': 'minerals', 'oasis': 'oasis',
}


def model_key(value: str) -> str:
    return (value or '').split('.')[-1]


def terrain_art_key(value: str) -> str:
    """Compatibility alias used by the main application."""
    return model_key(value)


class FreeColArt:
    def __init__(self, master):
        self.master = master
        self.base = None
        self.archive = None
        self.prefix = ''
        self.raw_cache = {}
        self.scaled_cache = {}
        self.status = 'FreeCol graphics not found — terrain labels shown instead.'
        self.find_installation()

    def find_installation(self):
        roots = [
            Path(r'C:\Program Files\FreeCol'),
            Path(r'C:\Program Files (x86)\FreeCol'),
            Path(r'C:\Programmer\FreeCol'),
            Path.home() / 'FreeCol',
            Path.cwd(),
        ]
        possible = [
            'app/data/default/resources/images',
            'data/default/resources/images',
            'default/resources/images',
            'resources/images',
            'data/base/resources/images',
        ]
        for root in roots:
            for rel in possible:
                img = root / rel
                if (img / 'terrain').is_dir():
                    self.base = img
                    self.status = f'FreeCol graphics: {img} (preview uses local textures with simple overlays)'
                    return
            if not root.is_dir():
                continue
            for arc in list(root.glob('*.jar')) + list(root.glob('*.zip')):
                try:
                    with zipfile.ZipFile(arc) as zf:
                        names = zf.namelist()
                        match = next((n for n in names if n.endswith('terrain/savannah/center0.size9.png')), None)
                        if not match:
                            match = next((n for n in names if n.endswith('terrain/savannah/center0.png')), None)
                    if match:
                        suffix = 'terrain/savannah/center0.size9.png' if match.endswith('center0.size9.png') else 'terrain/savannah/center0.png'
                        self.archive = arc
                        self.prefix = match[:-len(suffix)]
                        self.status = f'FreeCol graphics archive: {arc.name} (preview uses local textures with simple overlays)'
                        return
                except (OSError, zipfile.BadZipFile):
                    pass

    def _read_bytes(self, relpath):
        if self.base:
            fp = self.base / relpath
            if fp.is_file():
                return fp.read_bytes()
        if self.archive:
            try:
                with zipfile.ZipFile(self.archive) as zf:
                    return zf.read(self.prefix + relpath)
            except (OSError, KeyError, zipfile.BadZipFile):
                return None
        return None

    def _load_raw_image(self, key, candidates):
        if key in self.raw_cache:
            return self.raw_cache[key]
        raw = None
        for rel in candidates:
            raw = self._read_bytes(rel)
            if raw:
                break
        if not raw:
            self.raw_cache[key] = None
            return None
        try:
            img = tk.PhotoImage(master=self.master, data=base64.b64encode(raw).decode('ascii'))
        except tk.TclError:
            img = None
        self.raw_cache[key] = img
        return img

    def _scaled_image(self, img, cache_key, width, height):
        if img is None:
            return None
        if cache_key in self.scaled_cache:
            return self.scaled_cache[cache_key]
        ratio = min(width / max(1, img.width()), height / max(1, img.height()))
        if abs(ratio - 1) < 0.02:
            out = img
        else:
            pairs = [(a, b) for a in range(1, 10) for b in range(1, 16)]
            z, sub = min(pairs, key=lambda p: abs(p[0] / p[1] - ratio))
            out = img.zoom(z, z).subsample(sub, sub)
        self.scaled_cache[cache_key] = out
        return out

    def get(self, terrain_type, width=220, height=120):
        key = model_key(terrain_type)
        cache_key = ('terrain', key, int(width), int(height))
        if key in FOREST_KEYS:
            # The tree sprite is translucent and must never replace the ground tile.
            ground = {'scrubForest': 'savannah', 'broadleafForest': 'plains',
                      'coniferForest': 'grassland', 'mixedForest': 'grassland',
                      'tropicalForest': 'savannah', 'rainForest': 'grassland',
                      'wetlandForest': 'swamp', 'borealForest': 'tundra'}
            key = ground.get(key, 'grassland')
        base = TERRAIN_ALIASES.get(key, key)
        folder = base
        filename = 'center0.size9.png'
        if base == 'mountains':
            filename = 'mountains0.size9.png'
        elif base == 'hills':
            filename = 'hills0.size9.png'
        raw = self._load_raw_image(
            ('terrain', base),
            [
                f'terrain/{folder}/{filename}',
                f'terrain/{folder}/{filename.replace(".size9", "")}',
                f'terrain/{folder}/center0.size9.png',
                f'terrain/{folder}/center0.png',
            ],
        )
        return self._scaled_image(raw, cache_key, width, height) if raw is not None else None

    def get_bonus(self, resource_type, size=34):
        key = BONUS_KEYS.get(model_key(resource_type), model_key(resource_type))
        cache_key = ('bonus', key, int(size), int(size))
        raw = self._load_raw_image(
            ('bonus', key),
            [f'bonus/{key}.size9.png', f'bonus/{key}.png'],
        )
        return self._scaled_image(raw, cache_key, size, size) if raw is not None else None

    def get_forest(self, terrain_type, width, height):
        key = FOREST_KEYS.get(model_key(terrain_type))
        if not key:
            return None
        raw = self._load_raw_image(('forest', key), [
            f'forest/{key}/{key}.size9.png',
            f'forest/{key}/{key}.png',
            f'forest/{key}/{key}0000.size9.png',
            f'forest/{key}/{key}0000.png',
            f'forest/{key}/{key}1111.size9.png',
            f'forest/{key}/{key}1111.png',
        ])
        return self._scaled_image(raw, ('forest', key, int(width), int(height)), width, height) if raw else None

    def get_plowed(self, width, height):
        raw = self._load_raw_image(('improvement','plowed'), [
            'misc/plowed.png', 'misc/plowed.size9.png'])
        return self._scaled_image(raw, ('plowed',int(width),int(height)), width,height) if raw else None

    def get_river(self, style, width, height):
        """Load a native river sprite only when it exactly matches its saved style."""
        if len(style) != 4 or any(ch not in '012' for ch in style):
            return None
        raw = self._load_raw_image(('river-style', style), [
            f'river/river{style}.png',
            f'river/river{style}.size9.png',
            f'terrain/river/river{style}.png',
        ])
        return self._scaled_image(raw, ('river-style', style, int(width), int(height)), width, height) if raw else None
