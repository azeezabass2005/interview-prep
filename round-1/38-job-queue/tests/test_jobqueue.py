import unittest
from datetime import datetime

from jobqueue import JobQueue

T0 = datetime(2026, 5, 4, 12, 0, 0)


class TestJobQueue(unittest.TestCase):
    def test_lease_and_complete(self):
        q = JobQueue()
        q.enqueue("send-email", T0)
        job = q.lease("w1", T0)
        self.assertEqual(q.complete(job.job_id, "w1", T0).status, "DONE")


if __name__ == "__main__":
    unittest.main()
