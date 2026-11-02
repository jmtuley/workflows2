import unittest
from check import parse_variants


class VariantTests(unittest.TestCase):
    def product(self):
        return {"variants": [dict(id=i, options=[size, weight, fill], available=i % 2 == 0,
                                  price=57900 + i)
                             for i, (size, weight, fill) in enumerate(
                                 (s, w, f) for s in ("King", "Cal King")
                                 for w in ("Summer", "Light", "Medium", "Arctic")
                                 for f in ("700+ Goose Down", "850+ Goose Down"))]}

    def test_exact_king_weights_and_both_fills(self):
        rows = parse_variants(self.product(), "regular")
        self.assertEqual(len(rows), 6)
        self.assertEqual([r["id"] for r in rows], list(range(6)))
        self.assertEqual([r["available"] for r in rows], [True, False] * 3)
        self.assertEqual(rows[0]["price_cents"], 57900)

    def test_organic_excludes_summer(self):
        self.assertEqual([r["id"] for r in parse_variants(self.product(), "organic-seconds")], [2, 3, 4, 5])

    def test_missing_empty_and_duplicate_variants_fail(self):
        for variants in ([], self.product()["variants"][1:]):
            with self.subTest(variants=variants), self.assertRaises(ValueError):
                parse_variants({"variants": variants}, "regular")
        product = self.product()
        product["variants"].append(product["variants"][0])
        with self.assertRaises(ValueError):
            parse_variants(product, "regular")

    def test_invalid_price_and_availability_fail(self):
        for field, value in (("price", 0), ("price", "57900"), ("available", "false")):
            product = self.product()
            product["variants"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                parse_variants(product, "regular")


if __name__ == "__main__":
    unittest.main()
