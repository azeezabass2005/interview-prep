import unittest

from tests.helpers import World, always_fails


class TestQueue(unittest.TestCase):
    def setUp(self):
        self.w = World()
        self.ran = []
        self.w.registry.register("echo", lambda payload, ctx: self.ran.append(payload["msg"]))
        self.w.registry.register("broken", always_fails)

    def tearDown(self):
        self.w.cleanup()

    def test_submit_and_run(self):
        job_id = self.w.api.post_job({"kind": "echo", "payload": {"msg": "hi"}}).body["job_id"]
        self.assertEqual(self.w.worker().poll_once(), job_id)
        self.assertEqual(self.ran, ["hi"])
        self.assertEqual(self.w.api.get_job(job_id).body["status"], "DONE")

    def test_nothing_to_do(self):
        self.assertIsNone(self.w.worker().poll_once())

    def test_future_job_waits(self):
        self.w.api.post_job({"kind": "echo", "payload": {"msg": "later"}, "run_at": "2026-05-01T13:00:00+00:00"})
        self.assertIsNone(self.w.worker().poll_once())
        self.w.clock.advance(3600)
        self.assertIsNotNone(self.w.worker().poll_once())

    def test_run_at_requires_offset(self):
        self.assertEqual(self.w.api.post_job({"kind": "echo", "run_at": "2026-05-01T13:00:00"}).status, 400)

    def test_failure_is_retried_later(self):
        job_id = self.w.api.post_job({"kind": "broken"}).body["job_id"]
        self.w.worker().poll_once()
        body = self.w.api.get_job(job_id).body
        self.assertEqual((body["status"], body["attempts"]), ("PENDING", 1))
        self.assertIsNone(self.w.worker().poll_once())

    def test_crashed_worker_job_is_reclaimed(self):
        job_id = self.w.api.post_job({"kind": "echo", "payload": {"msg": "x"}}).body["job_id"]
        candidate = self.w.repo.next_candidate(self.w.clock.now())
        self.w.repo.claim(candidate, "crashed", self.w.clock.now(), self.w.clock.now())
        self.w.clock.advance(31)
        self.assertEqual(self.w.worker("w2").poll_once(), job_id)


if __name__ == "__main__":
    unittest.main()
