import threading
import unittest
from datetime import datetime
from unittest import mock

from blike.models import Commitment
from blike.repositories.commitments import CommitmentRepository
from blike.repositories.requests import RequestRepository
from blike.services.scoring import ScoringService
from tests.helpers import MONDAY, TUESDAY, TempDb, make_service, payload


def run_concurrently(*calls):
    """Run calls on threads; the first lookup of each call pauses until all have looked up."""
    barrier = threading.Barrier(len(calls), timeout=5)
    original = RequestRepository.find_by_key
    lookups = {"n": 0}
    lock = threading.Lock()

    def paused_find(repo, requester, key):
        result = original(repo, requester, key)
        with lock:
            lookups["n"] += 1
            first_round = lookups["n"] <= len(calls)
        if first_round:
            try:
                barrier.wait()
            except threading.BrokenBarrierError:
                pass
        return result

    results, errors = [None] * len(calls), []

    def worker(i, call):
        try:
            results[i] = call()
        except Exception as e:  # pragma: no cover - surfaced below
            errors.append(e)

    with mock.patch.object(RequestRepository, "find_by_key", paused_find):
        threads = [threading.Thread(target=worker, args=(i, c)) for i, c in enumerate(calls)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(10)
    if errors:
        raise errors[0]
    return results


class HiddenCalendar(unittest.TestCase):
    def setUp(self):
        self.tmp = TempDb()

    def tearDown(self):
        self.tmp.cleanup()

    def test_duplicate_request_overlapping_retries(self):
        a, b = make_service(self.tmp), make_service(self.tmp)
        r1, r2 = run_concurrently(lambda: a.submit_request("ea-app", "k-1", payload()),
                                  lambda: b.submit_request("ea-app", "k-1", payload()))
        self.assertEqual(r1.request_id, r2.request_id)
        self.assertEqual(RequestRepository(self.tmp.db).count(), 1)
        r3, r4 = run_concurrently(lambda: a.submit_request("ea-app", "k-2", payload()),
                                  lambda: b.submit_request("crm-sync", "k-2", payload()))
        self.assertNotEqual(r3.request_id, r4.request_id)

    def test_back_to_back_with_commitment(self):
        CommitmentRepository(self.tmp.db).add(
            Commitment("c1", "Board prep", datetime(2026, 5, 4, 10, 30), datetime(2026, 5, 4, 11, 0)))
        service = make_service(self.tmp)
        service.submit_request("ea-app", "k", payload(earliest="2026-05-04T10:00", latest="2026-05-04T11:30"))
        service.run_batch(MONDAY)
        _, meetings = service.schedule_for(MONDAY)
        self.assertEqual(meetings[0].start, datetime(2026, 5, 4, 10, 0))

    def test_vip_scoring_is_case_insensitive(self):
        self.assertEqual(ScoringService().score("CEO@bloomberg.example", "normal"), 60)
        self.assertEqual(ScoringService().score("cfo@bloomberg.example", "low"), 50)

    def test_no_request_left_pending(self):
        service = make_service(self.tmp)
        for i in range(6):
            service.submit_request("ea-app", f"k{i}", payload(title=f"m{i}"))
        service.run_batch(TUESDAY)
        statuses = [r.status for r in RequestRepository(self.tmp.db).all()]
        self.assertNotIn("PENDING", statuses)
