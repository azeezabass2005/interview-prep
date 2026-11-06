import unittest
from datetime import timedelta

from tests.helpers import NOW, World


class DigestTest(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_digest_lists_new_reports_in_entitled_sectors(self):
        self.w.client_user("org_hartwell", "usr_hal", sectors=["energy"])
        self.w.published("Oil outlook", "energy", NOW - timedelta(hours=3))
        self.w.published("Chip cycle", "tech", NOW - timedelta(hours=2))
        self.assertEqual(self.w.c.digest.schedule_all(), 1)
        self.w.c.worker.run_pending()
        self.assertEqual(len(self.w.email.calls), 1)
        sent = self.w.email.calls[0].json()
        self.assertEqual(sent["to"], "usr_hal@client.example")
        self.assertIn("Oil outlook", sent["html"])
        self.assertNotIn("Chip cycle", sent["html"])

    def test_nothing_new_sends_nothing(self):
        self.w.client_user("org_hartwell", "usr_hal", sectors=["energy"])
        self.w.c.digest.schedule_all()
        self.w.c.worker.run_pending()
        self.assertEqual(self.w.email.calls, [])

    def test_second_digest_only_has_newer_reports(self):
        self.w.client_user("org_hartwell", "usr_hal", sectors=["energy"])
        self.w.published("Oil outlook", "energy", NOW - timedelta(hours=3))
        self.w.c.digest.schedule_all()
        self.w.c.worker.run_pending()
        self.w.clock.advance(days=1)
        self.w.published("Gas storage", "energy")
        self.w.c.digest.schedule_all()
        self.w.c.worker.run_pending()
        second = self.w.email.calls[-1].json()["html"]
        self.assertIn("Gas storage", second)
        self.assertNotIn("Oil outlook", second)


if __name__ == "__main__":
    unittest.main()
