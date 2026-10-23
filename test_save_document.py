"""Headless Phase 0 SaveDocument contract tests."""
import tempfile
import unittest
import zipfile
from pathlib import Path
from save_document import SaveDocument


def save(xml):
    directory=tempfile.TemporaryDirectory()
    path=Path(directory.name)/"fixture.fsg"
    with zipfile.ZipFile(path,"w") as z:
        z.writestr("savegame.xml",xml)
    return directory,path


class SaveDocumentTests(unittest.TestCase):
    def test_loads_authoritative_records_excluding_cached_missionary(self):
        xml=b'''<freecol><game turn="155">
        <player id="player:1" ai="false" username="Tester"/>
        <map><tile id="tile:10" x="83" y="118">
        <colony id="colony:1" owner="player:1" name="Christiansborg">
          <unit id="unit:1" owner="player:1"/>
        </colony></tile>
        <tile id="tile:11" x="84" y="118">
          <indianSettlement id="indianSettlement:1" name="Xaymaca" owner="player:2">
          <missionary><unit id="unit:2" owner="player:1"/></missionary>
          </indianSettlement>
          <cachedTile><tile id="tile:11"><indianSettlement id="indianSettlement:1">
          <missionary><unit id="unit:2" owner="player:1"/></missionary>
          </indianSettlement></tile></cachedTile>
        </tile></map></game></freecol>'''
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"fixture.fsg"
            with zipfile.ZipFile(p,"w") as z:z.writestr("savegame.xml",xml)
            doc=SaveDocument.load(p)
            self.assertEqual(doc.turn,"155")
            self.assertEqual(len(doc.records["Units"]),2)
            self.assertEqual(len(doc.colonies),1)
            self.assertEqual(len(doc.native_settlements),1)
            self.assertEqual(doc.colony_tile_names["tile:10"],"Christiansborg")
            self.assertEqual(doc.terrain_by_xy[(83,118)].get("id"),"tile:10")

    def test_missing_game_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"fixture.fsg"
            with zipfile.ZipFile(p,"w") as z:z.writestr("savegame.xml",b"<freecol/>")
            with self.assertRaisesRegex(ValueError,"Missing <game>"):
                SaveDocument.load(p)

    def test_missing_xml_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"fixture.fsg"
            with zipfile.ZipFile(p,"w") as z:z.writestr("other.txt","hello")
            with self.assertRaisesRegex(ValueError,"no savegame.xml"):
                SaveDocument.load(p)


if __name__=="__main__":
    unittest.main()
