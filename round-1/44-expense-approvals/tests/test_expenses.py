import unittest
from decimal import Decimal

from expenses import Expenses, Item


class TestExpenses(unittest.TestCase):
    def test_small_report_manager_approves(self):
        e = Expenses({"ana": "mo"}, "dina", "carl")
        r = e.submit("ana", [Item("TAXI", Decimal("40"), receipt=True)])
        self.assertEqual(e.approve(r.report_id, "mo").status, "APPROVED")


if __name__ == "__main__":
    unittest.main()
