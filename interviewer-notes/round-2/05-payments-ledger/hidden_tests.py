import threading
import unittest
from unittest import mock

from ledger.errors import InsufficientFunds, LedgerError
from ledger.repositories.accounts import AccountRepository
from ledger.services.money import parse_amount
from tests.helpers import World


class HiddenLedger(unittest.TestCase):
    def setUp(self):
        self.w = World()
        self.w.wallets.open_account("A", "ann")
        self.w.wallets.open_account("B", "bob")

    def tearDown(self):
        self.w.cleanup()

    def test_PAY501_concurrent_withdrawals_cannot_overdraw(self):
        self.w.wallets.deposit("A", "100.00", "salary")
        s1, s2 = self.w.instance(), self.w.instance()
        barrier = threading.Barrier(2, timeout=3)
        original = AccountRepository.get
        calls = {"n": 0}
        lock = threading.Lock()

        def paused_get(repo, account_id):
            result = original(repo, account_id)
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

        def run(svc, ref):
            try:
                svc.withdraw("A", "80.00", ref)
                outcomes.append("ok")
            except InsufficientFunds:
                outcomes.append("insufficient")

        with mock.patch.object(AccountRepository, "get", paused_get):
            threads = [threading.Thread(target=run, args=(s1, "w1")), threading.Thread(target=run, args=(s2, "w2"))]
            for t in threads:
                t.start()
            for t in threads:
                t.join(10)
        self.assertEqual(sorted(outcomes), ["insufficient", "ok"])
        balance = self.w.wallets.get("A").balance_cents
        self.assertEqual(balance, 2000)
        self.assertEqual(self.w.entries.sum_for("A"), balance)

    def test_PAY502_failed_transfer_changes_nothing(self):
        self.w.wallets.deposit("A", "200.00", "salary")
        self.w.wallets.close_account("B")
        with self.assertRaises(LedgerError):
            self.w.wallets.transfer("A", "B", "50.00", "gift")
        self.assertEqual(self.w.wallets.get("A").balance_cents, 20000)
        self.assertEqual(self.w.entries.sum_for("A"), 20000)

    def test_PAY503_amounts_parse_exactly(self):
        self.assertEqual(parse_amount("8.20"), 820)
        self.assertEqual(parse_amount("4.35"), 435)
        with self.assertRaises(LedgerError):
            parse_amount("1.005")

    def test_PAY504_every_entry_once_across_pages(self):
        for i in range(5):
            self.w.wallets.deposit("A", "1.00", f"salary-{i}")  # same timestamp
        seen, cursor = [], None
        for _ in range(10):
            page = self.w.api.get_statement("A", cursor=cursor, limit=2).body
            seen += [e["reference"] for e in page["entries"]]
            cursor = page["next_cursor"]
            if cursor is None:
                break
        self.assertEqual(sorted(seen), [f"salary-{i}" for i in range(5)])
