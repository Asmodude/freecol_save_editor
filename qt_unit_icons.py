"""Read-only unit artwork from the user's installed FreeCol graphics.

No copyrighted assets are bundled. Exact unit-type filenames only; unknown
types receive an unmistakably neutral fallback instead of fabricated sprites.
"""
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap, QPolygonF
from pathlib import Path
import re
import zipfile
from freecol_art_source import discover, installation_roots


def unit_key(value):
    value = str(value or '').rsplit('.', 1)[-1].strip()
    if ' ' in value:
        words = value.split()
        value = words[0].lower() + ''.join(w[:1].upper() + w[1:] for w in words[1:])
    return value if value and value.replace('_', '').isalnum() else ''


class UnitIcons:
    def __init__(self, source=None):
        self.source = discover() if source is None else source
        self.cache = {}
        self._paths = None

    def _local_image(self, key, role=None):
        if self._paths is None:
            self._paths = self._index_images()
        names = (key + '.png', key + '.size0.png', key + '.size2.png')
        if role == 'dragoon':
            names = tuple('dragoon/' + name for name in names) + names
        for name in names:
            found = self._paths.get(name.casefold())
            if found is None:
                continue
            mode, root, path = found
            try:
                if mode == 'file':
                    return (root / path).read_bytes()
                with zipfile.ZipFile(root) as zf:
                    return zf.read(path)
            except (OSError, KeyError, zipfile.BadZipFile):
                continue
        return None

    def _index_images(self):
        base, archive, prefix, _ = self.source
        paths = {}
        roots = [Path(base)] if base else []
        if base is None and archive is None:
            for root in installation_roots():
                for rel in ('app/data/default/resources/images',
                            'data/default/resources/images',
                            'default/resources/images', 'resources/images'):
                    candidate = Path(root) / rel
                    if (candidate / 'units').is_dir():
                        roots.append(candidate)
        for root in roots:
            folder = root / 'units'
            if not folder.is_dir():
                continue
            for image in sorted(folder.rglob('*.png')):
                relative = image.relative_to(folder)
                paths.setdefault(relative.as_posix().casefold(), ('file', folder, relative))
                paths.setdefault(image.name.casefold(), ('file', folder, relative))
        if archive:
            try:
                with zipfile.ZipFile(archive) as zf:
                    for entry in sorted(zf.namelist()):
                        if entry.startswith(prefix + 'units/') and entry.lower().endswith('.png'):
                            relative = entry.split(prefix + 'units/', 1)[-1]
                            paths.setdefault(relative.casefold(), ('archive', archive, entry))
                            paths.setdefault(Path(entry).name.casefold(), ('archive', archive, entry))
            except (OSError, zipfile.BadZipFile):
                pass
        return paths

    def _resource_map(self):
        """Parse the installed FreeCol artwork manifest; never guess by filename."""
        if hasattr(self, '_manifest'):
            return self._manifest
        base, archive, prefix, _ = self.source
        data = None
        if base is not None:
            # base is normally .../resources/images
            base = Path(base)
            for candidate in (base.parent.parent / 'resources.properties',
                              base.parent / 'resources.properties'):
                if candidate.is_file():
                    data = candidate.read_bytes()
                    break
        if data is None and archive:
            try:
                with zipfile.ZipFile(archive) as zf:
                    for candidate in (prefix + 'resources.properties',
                                      prefix.removesuffix('resources/') + 'resources.properties',
                                      'data/default/resources.properties'):
                        if candidate in zf.namelist():
                            data = zf.read(candidate)
                            break
            except (OSError, zipfile.BadZipFile):
                pass
        mapping = {}
        if data:
            for line in data.decode('utf-8-sig', errors='replace').splitlines():
                line = line.strip()
                if not line or line.startswith(('#', '!')) or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                mapping[key.strip()] = value.strip()
        self._manifest = mapping
        return mapping

    def effective_icon(self, unit_type, role, size=23):
        """Follow FreeCol's image.unit.* mappings; never substitute generic role art."""
        manifest = self._resource_map()
        unit_id = str(unit_type or '')
        role_id = str(role or 'model.role.default').removeprefix('model.role.')
        keys = (f'image.unit.{unit_id}.{role_id}', f'image.unit.{unit_id}')
        base, archive, prefix, _ = self.source
        for key in keys:
            entry = manifest.get(key)
            if not entry:
                continue
            # Properties paths can contain optional image selectors after a comma.
            candidate = entry.split(',', 1)[0].strip().removeprefix('resource:')
            candidate = candidate.removeprefix('resources/images/').removeprefix('images/')
            if not candidate.startswith('units/'):
                continue
            data = None
            if base:
                file_path = Path(base) / candidate
                if file_path.is_file():
                    data = file_path.read_bytes()
            elif archive:
                try:
                    with zipfile.ZipFile(archive) as zf:
                        data = zf.read(prefix + candidate)
                except (OSError, KeyError, zipfile.BadZipFile):
                    pass
            if data:
                pix = QPixmap()
                if pix.loadFromData(data) and not pix.isNull():
                    return QIcon(pix)
        # No authoritative mapping available: retain the unit's own exact
        # type art rather than guessing a role from a coincidentally named file.
        return self.icon(unit_type, size=size)

    def icon(self, value, size=23, role=None):
        key = unit_key(value)
        if not key:
            return QIcon()
        role_key = unit_key(role).casefold()
        cache_key = (key, size, role_key)
        if cache_key in self.cache:
            return self.cache[cache_key]
        data = self._local_image(key, role_key)
        if data:
            pix = QPixmap()
            if pix.loadFromData(data) and not pix.isNull():
                result = QIcon(pix)
                self.cache[cache_key] = result
                return result
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor('#b67b46'))
        painter.setPen(QPen(QColor('#503f35'), max(1, size * .07)))
        painter.drawEllipse(QRectF(size*.34, size*.10, size*.32, size*.27))
        painter.drawPolygon(QPolygonF([
            QPointF(size*.29, size*.42),
            QPointF(size*.70, size*.42),
            QPointF(size*.79, size*.86),
            QPointF(size*.20, size*.86)]))
        painter.end()
        result = QIcon(pix)
        self.cache[cache_key] = result
        return result
