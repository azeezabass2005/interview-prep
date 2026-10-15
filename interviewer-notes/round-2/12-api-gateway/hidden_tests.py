import unittest

from tests.helpers import World, call


class HiddenGateway(unittest.TestCase):
    def setUp(self):
        self.w = World()

    def tearDown(self):
        self.w.cleanup()

    def test_GW1201_limit_shared_across_instances(self):
        gateways = [self.w.gateway(), self.w.gateway(), self.w.gateway()]
        statuses = [call(gateways[i % 3], "k-acme-admin").status for i in range(61)]
        self.assertEqual(statuses.count(200), 60)

    def test_GW1202_tenants_are_isolated(self):
        gw = self.w.gateway()
        for _ in range(61):
            call(gw, "k-acme-admin")
        self.assertEqual(call(gw, "k-globex-admin").status, 200)

    def test_GW1203_retry_after_is_time_left_in_window(self):
        gw = self.w.gateway()
        self.w.clock.advance(15.2)
        responses = [call(gw, "k-acme-admin") for _ in range(61)]
        self.assertEqual(responses[-1].headers["Retry-After"], "45")

    def test_GW1204_plan_change_applies_within_ttl(self):
        gw = self.w.gateway()
        call(gw, "k-initech")
        self.w.tenants.upsert("initech", "pro")
        self.w.clock.advance(61)
        statuses = [call(gw, "k-initech").status for _ in range(61)]
        self.assertEqual(statuses.count(200), 61)
