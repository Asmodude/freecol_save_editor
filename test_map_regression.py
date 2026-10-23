"""Headless regression tests for the accepted staggered-row map geometry.

No Tkinter, save files, or installed artwork are required.
"""
import unittest

from map_geometry import map_grid, neighbor


class MapGeometryRegressionTests(unittest.TestCase):
    def test_neighborhood_has_eighty_one_unique_coordinates(self):
        for center in ((83, 118), (69, 111), (67, 110), (79, 122)):
            items = list(map_grid(*center))
            self.assertEqual(len(items), 81)
            self.assertEqual(len({(x, y) for _, _, x, y in items}), 81)
            self.assertEqual(next((x, y) for r, c, x, y in items if r == c == 0), center)

    def test_directional_neighbors_reverse(self):
        for coordinate in ((83, 118), (69, 111), (67, 110)):
            for forward, reverse in (("NE", "SW"), ("SE", "NW")):
                self.assertEqual(
                    neighbor(*neighbor(*coordinate, forward), reverse),
                    coordinate,
                )

    def test_christiansborg_even_row_neighbours(self):
        point = (83, 118)
        self.assertEqual(neighbor(*point, "NE"), (83, 117))
        self.assertEqual(neighbor(*point, "SE"), (83, 119))
        self.assertEqual(neighbor(*point, "SW"), (82, 119))
        self.assertEqual(neighbor(*point, "NW"), (82, 117))

    def test_major_river_odd_row_neighbours(self):
        point = (69, 111)
        self.assertEqual(neighbor(*point, "NE"), (70, 110))
        self.assertEqual(neighbor(*point, "SE"), (70, 112))
        self.assertEqual(neighbor(*point, "SW"), (69, 112))
        self.assertEqual(neighbor(*point, "NW"), (69, 110))

    def test_tile_edges_share_vertices_in_screen_space(self):
        tile_width = 100
        tile_height = 50
        for cx, cy in ((83, 118), (69, 111)):
            coords = {(x, y): (r, c) for r, c, x, y in map_grid(cx, cy)}
            def polygon(r, c):
                px = (r + c) * tile_width / 2
                py = (r - c) * tile_height / 2
                return {
                    (px, py - tile_height / 2), (px + tile_width / 2, py),
                    (px, py + tile_height / 2), (px - tile_width / 2, py),
                }
            for (x, y), (r, c) in coords.items():
                for direction in ("NE", "SE", "SW", "NW"):
                    other = coords.get(neighbor(x, y, direction))
                    if other is not None:
                        self.assertEqual(
                            len(polygon(r, c) & polygon(*other)), 2,
                            (cx, cy, (x, y), direction),
                        )


if __name__ == "__main__":
    unittest.main()
