import unittest

from bonds.app import build_app


class TestBonds(unittest.TestCase):
    def test_book_midweek(self):
        api, _ = build_app()
        api.load_bond({"bond_id": "B1", "coupon": "0.05", "frequency": 2, "maturity": "2030-05-15"})
        status, trade = api.book({"trade_id": "T1", "bond_id": "B1", "face": "1000000", "price": "100",
                                  "trade_date": "2026-01-14"})
        self.assertEqual(status, 201)
        self.assertEqual((trade["settle_date"], trade["accrued"]), ("2026-01-15", "8333.33"))


if __name__ == "__main__":
    unittest.main()
