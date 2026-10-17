import unittest
from datetime import datetime

from fx.app import build_app


class FakeClock:
    def __init__(self):
        self.current = datetime(2026, 4, 1, 12, 0, 0)

    def now(self):
        return self.current


class TestFx(unittest.TestCase):
    def test_eur_to_usd_quote_and_book(self):
        api = build_app(FakeClock())
        api.publish("EURUSD", "1.0850")
        status, quote = api.quote({"customer": "c1", "source": "EUR", "amount": "1000", "target": "USD"})
        self.assertEqual((status, quote["target_amount"]), (201, "1074.15"))
        self.assertEqual(api.book(quote["quote_id"])[0], 201)


if __name__ == "__main__":
    unittest.main()
