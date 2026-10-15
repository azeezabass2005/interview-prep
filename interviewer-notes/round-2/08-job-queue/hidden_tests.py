import unittest

from jobq.handlers_registry import HandlerRegistry
from jobq.services.backoff import retry_delay_seconds
from tests.helpers import World, always_fails


class HiddenJobs(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_JOB801_heartbeat_keeps_lease(self):
        other_ran = []
        other_registry = HandlerRegistry()
        other_registry.register("statement", lambda payload, ctx: other_ran.append(ctx.job.job_id))
        second = self.w.worker("w2", other_registry)
        observed = {}

        def long_job(payload, ctx):
            self.w.clock.advance(20)
            ctx.heartbeat()
            self.w.clock.advance(15)
            observed["second_poll"] = second.poll_once()
            self.w.clock.advance(10)

        self.w.registry.register("statement", long_job)
        job_id = self.w.api.post_job({"kind": "statement"}).body["job_id"]
        self.w.worker("w1").poll_once()
        self.assertIsNone(observed["second_poll"])
        self.assertEqual(other_ran, [])
        self.assertEqual(self.w.repo.run_count(job_id), 1)

    def test_JOB802_exponential_backoff_with_cap(self):
        self.assertEqual([retry_delay_seconds(a) for a in range(1, 7)], [30, 60, 120, 240, 480, 600])
        self.assertEqual(retry_delay_seconds(12), 600)

    def test_JOB803_max_attempts_is_a_hard_limit(self):
        self.w.registry.register("email", always_fails)
        job_id = self.w.api.post_job({"kind": "email", "max_attempts": 3}).body["job_id"]
        for _ in range(6):
            self.w.worker().poll_once()
            self.w.clock.advance(700)
        self.assertEqual(self.w.repo.run_count(job_id), 3)
        self.assertEqual(self.w.api.get_job(job_id).body["status"], "DEAD")

    def test_JOB804_run_at_offset_respected(self):
        ran = []
        self.w.registry.register("publish", lambda payload, ctx: ran.append(1))
        job_id = self.w.api.post_job({"kind": "publish", "run_at": "2026-05-01T09:00:00-04:00"}).body["job_id"]
        self.assertEqual(self.w.api.get_job(job_id).body["run_at"], "2026-05-01T13:00:00Z")
        self.assertIsNone(self.w.worker().poll_once())  # 12:00 UTC
        self.w.clock.advance(3600)
        self.assertEqual(self.w.worker().poll_once(), job_id)
        london = self.w.api.post_job({"kind": "publish", "run_at": "2026-05-01T14:30:00+01:00"}).body["job_id"]
        self.assertEqual(self.w.api.get_job(london).body["run_at"], "2026-05-01T13:30:00Z")
