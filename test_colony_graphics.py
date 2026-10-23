import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from colony_graphics import resolve_colony_graphic, population_size

class ColonyGraphicsTests(unittest.TestCase):
    def colony(self, population, building=None, owner="player:19"):
        e=ET.Element("colony",{"owner":owner})
        for i in range(population):
            ET.SubElement(e,"unit",{"id":f"unit:{i}"})
        if building:
            ET.SubElement(e,"building",{"buildingType":"model.building."+building})
        return e

    def test_all_twelve_states(self):
        for size,pop in (("small",2),("medium",5),("large",9)):
            for tier,building in (("colony",None),("stockade","stockade"),("fort","fort"),("fortress","fortress")):
                g=resolve_colony_graphic(self.colony(pop,building))
                self.assertEqual(g.key,f"{tier}_{size}")
                self.assertEqual(g.population,pop)
                self.assertIsNone(g.image_path)

    def test_nationality_does_not_change_artwork(self):
        a=resolve_colony_graphic(self.colony(5,"fort","player:19"))
        b=resolve_colony_graphic(self.colony(5,"fort","player:136"))
        self.assertEqual(a.key,b.key)

    def test_fortification_highest_tier(self):
        e=self.colony(9,"stockade")
        ET.SubElement(e,"building",{"buildingType":"model.building.fortress"})
        self.assertEqual(resolve_colony_graphic(e).key,"fortress_large")

    def test_real_savegame_building_type_attribute(self):
        # Morten(5).fsg: both colonies have six working units; Christiansborg
        # has a fort, while Frederiksborg has no fortification building.
        unfortified=self.colony(6)
        fortified=self.colony(6,"fort")
        self.assertEqual(resolve_colony_graphic(unfortified).key,"colony_medium")
        self.assertEqual(resolve_colony_graphic(fortified).key,"fort_medium")

    def test_missing_fort_art_does_not_fall_back_to_unfortified(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/"colony_medium.png").write_bytes(b"dummy")
            resolved=resolve_colony_graphic(self.colony(6,"fort"),asset_dir=tmp)
            self.assertEqual(resolved.key,"fort_medium")
            self.assertIsNone(resolved.image_path)

    def test_asset_lookup(self):
        with tempfile.TemporaryDirectory() as tmp:
            image=Path(tmp)/"fort_medium.png"
            image.write_bytes(b"dummy")
            g=resolve_colony_graphic(self.colony(5,"fort"),asset_dir=tmp)
            self.assertEqual(g.image_path,image)

if __name__=="__main__":
    unittest.main()
