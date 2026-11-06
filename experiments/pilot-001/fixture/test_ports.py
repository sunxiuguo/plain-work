import unittest
from ports import parse_port

class PortTests(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(parse_port('80'), 80)

    def test_whitespace(self):
        self.assertEqual(parse_port(' 443 '), 443)

    def test_invalid(self):
        for raw in ('0', '65536', 'abc'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_port(raw)

if __name__ == '__main__':
    unittest.main()
