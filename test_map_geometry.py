import unittest
from map_geometry import map_grid, neighbor

class GridTests(unittest.TestCase):
    def test_cardinality_and_topology(self):
        for centre in ((67,110),(69,111),(83,118)):
            positions={(r,c):(x,y) for r,c,x,y in map_grid(*centre)}
            self.assertEqual(len(positions),81)
            self.assertEqual(len(set(positions.values())),81)
            self.assertEqual(positions[0,0],centre)
            for (r,c),(x,y) in positions.items():
                if (r+1,c) in positions:
                    self.assertEqual(positions[r+1,c],neighbor(x,y,'SE'))
                if (r,c+1) in positions:
                    self.assertEqual(positions[r,c+1],neighbor(x,y,'NE'))

    def test_shared_diamond_edges(self):
        w,h=200,100
        for r in range(-4,5):
            for c in range(-4,5):
                x,y=(r+c)*w/2,(r-c)*h/2
                if r<4:
                    xx,yy=(r+c+1)*w/2,(r-c+1)*h/2
                    self.assertEqual((x,y+h/2),(xx-w/2,yy))
                    self.assertEqual((x+w/2,y),(xx,yy-h/2))
                if c<4:
                    xx,yy=(r+c+1)*w/2,(r-c-1)*h/2
                    self.assertEqual((x,y-h/2),(xx-w/2,yy))
                    self.assertEqual((x+w/2,y),(xx,yy+h/2))

if __name__=='__main__':
    unittest.main()
