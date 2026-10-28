"""Optional FreeCol Hammers probe parser must fail closed."""
import unittest
from types import SimpleNamespace
from xml.etree.ElementTree import fromstring

from qt_hammer_probe import parse_hammer_probe, HammerProbeError

HEADER = 'FREECOL_HAMMERS_V1\tcolony_id\towner_id\tgross\tnet'


class HammerProbeTests(unittest.TestCase):
    def setUp(self):
        self.doc = SimpleNamespace(colonies=[
            fromstring('<colony id="colony:1" owner="player:1"/>'),
            fromstring('<colony id="colony:2" owner="player:1"/>'),
        ])

    def test_valid_gross_and_net_are_distinct(self):
        output = HEADER + '\ncolony:1\tplayer:1\t12\t9\ncolony:2\tplayer:1\t0\t-2'
        result = parse_hammer_probe(output, self.doc)
        self.assertEqual(result['colony:1'].gross, 12)
        self.assertEqual(result['colony:1'].net, 9)
        self.assertEqual(result['colony:2'].gross, 0)
        self.assertEqual(result['colony:2'].net, -2)

    def test_bad_output_is_rejected(self):
        invalid = (
            'WRONG\ncolony:1\tplayer:1\t12\t9',
            HEADER + '\ncolony:1\tplayer:2\t12\t9\ncolony:2\tplayer:1\t0\t0',
            HEADER + '\ncolony:1\tplayer:1\t12\t9',
            HEADER + '\ncolony:1\tplayer:1\t12\t9\ncolony:1\tplayer:1\t0\t0',
            HEADER + '\ncolony:1\tplayer:1\t5.5\t9\ncolony:2\tplayer:1\t0\t0',
            HEADER + '\ncolony:1\tplayer:1\t12\t9\ncolony:2\tplayer:1\t0\t999999999999999999999',
        )
        for output in invalid:
            with self.subTest(output=output[:50]):
                with self.assertRaises(HammerProbeError):
                    parse_hammer_probe(output, self.doc)


if __name__ == '__main__':
    unittest.main()
