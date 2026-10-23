"""Tk-independent map rendering contract checks."""
import unittest
import map_render


class MapRenderTests(unittest.TestCase):
    def test_even_odd_tile_offsets(self):
        self.assertEqual(map_render.terrain_offsets(118)['NE'],(0,-1))
        self.assertEqual(map_render.terrain_offsets(111)['NE'],(1,-1))
        self.assertEqual(len(map_render.terrain_offsets(118)),9)

    def test_diamond_geometry(self):
        self.assertTrue(map_render.diamond_contains(0,0,0,0,100,50))
        self.assertTrue(map_render.diamond_contains(50,0,0,0,100,50))
        self.assertFalse(map_render.diamond_contains(51,0,0,0,100,50))
        self.assertFalse(map_render.diamond_contains(0,0,0,0,0,50))

    def test_road_styles_and_exact_original_instructions(self):
        self.assertEqual(map_render.road_primitives(0,0,100,50,'00000000'),[])
        self.assertEqual(map_render.road_primitives(0,0,100,50,'X0000000'),[])
        strokes=map_render.road_primitives(0,0,100,50,'10000000')
        self.assertEqual(len(strokes),3)
        self.assertEqual(strokes[0],('line',(0,0,0.0,-14.5,0.0,-25.0),
                                      {'fill':'#714d2e','width':3,'smooth':1}))
        self.assertEqual(strokes[1][2]['fill'],'#c99b61')
        self.assertEqual(strokes[2][0],'oval')

    def test_river_style_2220(self):
        strokes=map_render.river_primitives(0,0,100,50,'2220')
        self.assertEqual(len(strokes),6)
        self.assertEqual(strokes[0][2],{'fill':'#3d7189','width':6,'smooth':1})
        self.assertEqual(strokes[1][2],{'fill':'#8dc4da','width':4,'smooth':1})
        self.assertEqual(map_render.river_primitives(0,0,100,50,'bogus'),[])


if __name__=='__main__':
    unittest.main()
