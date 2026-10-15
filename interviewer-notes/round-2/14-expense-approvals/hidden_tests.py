import threading
import unittest
from unittest import mock

from expenses.errors import InvalidState
from expenses.repositories.expenses import ExpenseRepository
from tests.helpers import World


class HiddenExpenses(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_EXP1401_concurrent_approvals_pay_once(self):
        eid = self.w.submit()
        a, b = self.w.workflow(), self.w.workflow()
        barrier = threading.Barrier(2, timeout=3)
        original = ExpenseRepository.get
        calls = {"n": 0}
        lock = threading.Lock()

        def paused(repo, expense_id):
            result = original(repo, expense_id)
            with lock:
                calls["n"] += 1
                first = calls["n"] <= 2
            if first:
                try:
                    barrier.wait()
                except threading.BrokenBarrierError:
                    pass
            return result

        outcomes = []

        def run(svc):
            try:
                outcomes.append(svc.approve(eid, "mark"))
            except InvalidState:
                outcomes.append("conflict")

        with mock.patch.object(ExpenseRepository, "get", paused):
            threads = [threading.Thread(target=run, args=(s,)) for s in (a, b)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(10)
        self.assertEqual(sorted(outcomes), ["APPROVED", "conflict"])
        self.assertEqual(self.w.payments.count_for(eid), 1)

    def test_EXP1402_threshold_in_usd_inclusive(self):
        eur = self.w.submit(amount="4800", currency="EUR")
        self.assertEqual(self.w.api.post_approve(eur, "mark").body["status"], "PENDING_DIRECTOR")
        exact = self.w.submit(amount="5000.00")
        self.assertEqual(self.w.api.post_approve(exact, "mark").body["status"], "PENDING_DIRECTOR")

    def test_EXP1403_no_self_approval(self):
        eid = self.w.submit(who="mark", amount="200")
        self.assertEqual(self.w.api.post_approve(eid, "mark").status, 403)
        self.assertEqual(self.w.api.post_approve(eid, "mia").body["status"], "APPROVED")
        big = self.w.submit(who="dora", amount="9000")
        self.w.api.post_approve(big, "mark")
        self.assertEqual(self.w.api.post_approve(big, "dora").status, 403)

    def test_EXP1404_report_converts_to_usd(self):
        self.w.submit(amount="100.00", currency="USD")
        self.w.submit(amount="100.00", currency="EUR")
        self.w.submit(amount="100.00", currency="GBP")
        self.assertEqual(self.w.api.get_team_report("london", 2026, 3).body["total_usd"], "335.50")
