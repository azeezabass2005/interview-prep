import unittest
from datetime import datetime

from blike.models import Commitment
from blike.repositories.commitments import CommitmentRepository
from tests.helpers import TUESDAY, TempDb, make_service, payload


class TestBatch(unittest.TestCase):
    def setUp(self):
        self.tmp = TempDb()
        self.service = make_service(self.tmp)

    def tearDown(self):
        self.tmp.cleanup()

    def test_single_request_scheduled_at_start_of_day(self):
        req = self.service.submit_request("ea-app", "k1", payload())
        result = self.service.run_batch(TUESDAY)
        self.assertEqual(result.scheduled, 1)
        self.assertEqual(self.service.get_request(req.request_id).status, "SCHEDULED")

    def test_avoids_protected_commitment(self):
        CommitmentRepository(self.tmp.db).add(
            Commitment("c1", "Offsite", datetime(2026, 5, 5, 9, 0), datetime(2026, 5, 5, 12, 0)))
        self.service.submit_request("ea-app", "k1", payload())
        self.service.run_batch(TUESDAY)
        _, meetings = self.service.schedule_for(TUESDAY)
        self.assertGreaterEqual(meetings[0].start, datetime(2026, 5, 5, 12, 0))

    def test_unschedulable_when_window_full(self):
        CommitmentRepository(self.tmp.db).add(
            Commitment("c1", "All day", datetime(2026, 5, 5, 9, 0), datetime(2026, 5, 5, 18, 0)))
        req = self.service.submit_request("ea-app", "k1", payload())
        self.service.run_batch(TUESDAY)
        self.assertEqual(self.service.get_request(req.request_id).status, "UNSCHEDULABLE")


if __name__ == "__main__":
    unittest.main()
