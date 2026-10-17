import unittest
from decimal import Decimal

from expenses import Expenses, Item


def expenses():
    return Expenses({"ana": "mo", "mo": "dina", "dina": "carl"}, "dina", "carl")


def hotel(amount):
    return [Item("HOTEL", Decimal(amount), receipt=True, justification="conference")]


class HiddenExpenses(unittest.TestCase):
    def test_B1_exactly_500_needs_only_manager(self):
        r = expenses().submit("ana", hotel("200") + hotel("200") + hotel("100"))
        self.assertEqual(r.chain, ["mo"])

    def test_B2_receipt_from_25(self):
        with self.assertRaises(Exception):
            expenses().submit("ana", [Item("TAXI", Decimal("25.00"))])

    def test_B3_own_step_skipped(self):
        e = expenses()
        r = e.submit("dina", hotel("200") + hotel("220") + hotel("200"))
        e.approve(r.report_id, "carl")
        self.assertEqual(r.status, "APPROVED")

    def test_B4_approvals_in_order(self):
        e = expenses()
        r = e.submit("ana", hotel("200") + hotel("220") + hotel("200"))
        with self.assertRaises(Exception):
            e.approve(r.report_id, "dina")

    def test_B5_resubmit_restarts_chain(self):
        e = expenses()
        r = e.submit("ana", hotel("200") + hotel("220") + hotel("200"))
        e.approve(r.report_id, "mo")
        e.reject(r.report_id, "dina")
        e.resubmit(r.report_id, hotel("200") + hotel("220") + hotel("190"))
        self.assertEqual(e.pending_approver(r.report_id), "mo")
