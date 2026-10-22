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
            ET.SubElement(e,"building",{"type":"model.building."+building})
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
        ET.SubElement(e,"building",{"type":"model.building.fortress"})
        self.assertEqual(resolve_colony_graphic(e).key,"fortress_large")

    def test_asset_lookup(self):
        with tempfile.TemporaryDirectory() as tmp:
            image=Path(tmp)/"fort_medium.png"
            image.write_bytes(b"dummy")
            g=resolve_colony_graphic(self.colony(5,"fort"),asset_dir=tmp)
            self.assertEqual(g.image_path,image)

if __name__=="__main__":
    unittest.main()
