import unittest
from decimal import Decimal

from margin.app import build_app

RUN = "2026-06-10"


def world(cash, positions, prices, classes):
    api = build_app()
    for symbol, cls in classes.items():
        api.add_security(symbol, cls)
    for symbol, (on, px) in prices.items():
        api.price(symbol, on, px)
    api.open_account("A", cash, positions)
    return api


EXAMPLE = dict(positions={"AAPL": 400, "TLT": 300, "SPY": 50},
               classes={"AAPL": "EQUITY", "TLT": "BOND", "SPY": "ETF"})


class HiddenMargin(unittest.TestCase):
    def test_B1_concentration_uses_gross_long(self):
        api = world("0", {"A1": 300, "B1": 380, "C1": 320, "S1": -200},
                    {s: (RUN, "100") for s in ("A1", "B1", "C1", "S1")}, {s: "EQUITY" for s in ("A1", "B1", "C1", "S1")})
        self.assertEqual(Decimal(api.run("A", RUN)[1]["collateral"]), Decimal("75000"))

    def test_B2_short_requirement_includes_principal(self):
        api = world("0", {"S1": -100}, {"S1": (RUN, "100")}, {"S1": "EQUITY"})
        self.assertEqual(Decimal(api.run("A", RUN)[1]["requirement"]), Decimal("13000"))

    def test_B3_call_rounds_up(self):
        api = world("-100040", EXAMPLE["positions"], {"AAPL": (RUN, "200"), "TLT": (RUN, "100"), "SPY": (RUN, "400")},
                    EXAMPLE["classes"])
        self.assertEqual(Decimal(api.run("A", RUN)[1]["call"]["amount"]), Decimal("16100"))

    def test_B4_stale_surcharge_after_concentration(self):
        api = world("-100000", EXAMPLE["positions"],
                    {"AAPL": ("2026-06-08", "200"), "TLT": (RUN, "100"), "SPY": (RUN, "400")}, EXAMPLE["classes"])
        self.assertEqual(Decimal(api.run("A", RUN)[1]["call"]["amount"]), Decimal("24000"))

    def test_B5_only_deposits_after_call_count(self):
        api = world("-105000", EXAMPLE["positions"], {"AAPL": ("2026-06-01", "200"), "TLT": ("2026-06-01", "100"),
                                                      "SPY": ("2026-06-01", "400")}, EXAMPLE["classes"])
        api.deposit("A", "2026-06-01", "5000")
        api.price("AAPL", RUN, "200")
        api.price("TLT", RUN, "100")
        api.price("SPY", RUN, "400")
        self.assertEqual(Decimal(api.run("A", RUN)[1]["call"]["amount"]), Decimal("16000"))
        api.deposit("A", "2026-06-11", "12000")
        self.assertEqual(api.call_status("A")[1]["calls"][0]["status"], "OPEN")
