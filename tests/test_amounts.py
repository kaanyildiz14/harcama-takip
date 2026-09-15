import unittest

from amounts import tutar_dogrula


class AmountTests(unittest.TestCase):
    def test_valid_amounts(self):
        for value, expected in [("12,50", 12.5), (" 12.50 ", 12.5), (1, 1.0)]:
            with self.subTest(value=value):
                self.assertEqual(tutar_dogrula(value), expected)

    def test_invalid_amounts(self):
        for value in ["nan", "NaN", "inf", "-inf", "1e309", 0, -1,
                      "", "abc", "1.234,56", None, float("nan"), float("inf")]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    tutar_dogrula(value)
