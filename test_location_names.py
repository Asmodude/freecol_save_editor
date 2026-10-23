import unittest
import xml.etree.ElementTree as ET

from location_names import colony_tile_names, location_label


class LocationNameTests(unittest.TestCase):
    def test_colony_tile_uses_name_not_coordinates(self):
        game=ET.fromstring("""<game><map>
          <tile id="tile:12611" x="79" y="122">
            <colony id="colony:5" name="Taphus"/>
          </tile>
          <tile id="tile:2" x="80" y="122"/>
        </map></game>""")
        names=colony_tile_names(game)
        tiles={"tile:12611":("79","122"),"tile:2":("80","122")}
        self.assertEqual(location_label("tile:12611",{},tiles,names),"Taphus")
        self.assertEqual(location_label("tile:2",{},tiles,names),"Tile (80,122)")

    def test_cached_colony_cannot_override_authoritative_name(self):
        game=ET.fromstring("""<game><map>
          <tile id="tile:1"><colony id="colony:1" name="Christiansborg"/></tile>
          <tile id="tile:2"><cachedTile><tile id="tile:1">
            <colony id="colony:1" name="Wrong cached name"/>
          </tile></cachedTile></tile>
        </map></game>""")
        self.assertEqual(colony_tile_names(game),{"tile:1":"Christiansborg"})

    def test_direct_location_id_still_resolves(self):
        self.assertEqual(location_label("colony:1",{"colony:1":"Frederiksborg"},{},{}),"Frederiksborg")

    def test_ambiguous_colony_placement_rejected(self):
        game=ET.fromstring("""<game><map><tile id="tile:1">
          <colony id="colony:1" name="A"/><colony id="colony:2" name="B"/>
        </tile></map></game>""")
        with self.assertRaisesRegex(ValueError,"Ambiguous"):
            colony_tile_names(game)


if __name__=="__main__":
    unittest.main()
