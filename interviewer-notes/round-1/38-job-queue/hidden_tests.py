import unittest
from datetime import datetime, timedelta

from jobqueue import JobQueue

T0 = datetime(2026, 5, 4, 12, 0, 0)


class HiddenJobQueue(unittest.TestCase):
    def test_B1_priority_one_first(self):
        q = JobQueue()
        q.enqueue("report", T0, priority=5)
        q.enqueue("fraud-check", T0, priority=1)
        self.assertEqual(q.lease("w1", T0).name, "fraud-check")

    def test_B2_delayed_jobs_wait(self):
        q = JobQueue()
        q.enqueue("later", T0, run_at=T0 + timedelta(seconds=60))
        self.assertIsNone(q.lease("w1", T0))

    def test_B3_expired_lease_can_be_retaken(self):
        q = JobQueue()
        q.enqueue("send-email", T0)
        q.lease("w1", T0)
        job = q.lease("w2", T0 + timedelta(seconds=31))
        self.assertEqual(job.worker if job else None, "w2")

    def test_B4_dead_only_after_max_attempts(self):
        q = JobQueue()
        job = q.enqueue("send-email", T0)
        now = T0
        for _ in range(2):
            q.lease("w1", now)
            q.fail(job.job_id, "w1", now)
            now = job.run_at
        self.assertEqual(job.status, "PENDING")

    def test_B5_only_lease_holder_can_complete(self):
        q = JobQueue()
        job = q.enqueue("send-email", T0)
        q.lease("w1", T0)
        with self.assertRaises(Exception):
            q.complete(job.job_id, "w2", T0)
