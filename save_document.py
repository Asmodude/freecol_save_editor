"""UI-independent FreeCol save loading and authoritative indexing.

Phase 0: exact extraction of accepted v0.6.2.6.4 load semantics.
"""
import collections
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
from location_names import colony_tile_names, unit_locations
from unit_records import authoritative_units


class SaveDocument:
    @classmethod
    def load(cls, path):
        with zipfile.ZipFile(path) as z:
            if 'savegame.xml' not in z.namelist():
                raise ValueError('Archive has no savegame.xml.')
            xml_bytes=z.read('savegame.xml')
            root=ET.fromstring(xml_bytes)
        game=root.find('game')
        if game is None:
            raise ValueError('Missing <game> node.')
        players={p.get('id'):p for p in game.findall('player')}
        colonies=[e for e in game.findall('./map/tile/colony') if (e.get('id') or '').startswith('colony:')]
        if len(colonies)!=len({e.get('id') for e in colonies}):
            raise ValueError('Duplicate authoritative colony IDs')
        natives=[e for e in game.findall('./map/tile/indianSettlement') if (e.get('id') or '').startswith('indianSettlement:')]
        if len(natives)!=len({e.get('id') for e in natives}):
            raise ValueError('Duplicate authoritative native settlement IDs')
        units=authoritative_units(game)
        self=cls()
        self.path=Path(path)
        self.xml_bytes=xml_bytes
        self.root=root
        self.game=game
        self.players=players
        self.colonies=colonies
        self.native_settlements=natives
        self.units=units
        self.locations={e.get('id'):e.get('name','') for e in colonies+natives}
        self.tiles={e.get('id'):(e.get('x'),e.get('y')) for e in game.iter('tile') if 'x' in e.attrib}
        self.colony_tile_names=colony_tile_names(game)
        self.unit_locations=unit_locations(units)
        self.colony_counts=collections.Counter(e.get('owner') for e in colonies)
        self.native_counts=collections.Counter(e.get('owner') for e in natives)
        self.professions=sorted({e.get('learnableSkill') for e in natives if e.get('learnableSkill')})
        self.goods_types=sorted({g.get('type') for g in game.iter('goods') if g.get('type')} | {g.get('id') for g in root.iter('goods-type') if g.get('id')})
        self.records={'Players':list(players.values()),'Colonies':colonies,
                      'Native settlements':natives,'Units':units}
        self.terrain_by_xy={(int(t.get('x')),int(t.get('y'))):t for t in game.findall('./map/tile') if t.get('x') is not None and t.get('y') is not None}
        self.turn=game.get('turn')
        return self
