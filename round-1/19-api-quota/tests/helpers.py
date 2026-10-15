from decimal import Decimal

from quota.limiter import RateLimiter


class FakeClock:
    def __init__(self):
        self.t = Decimal(0)

    def now(self):
        return self.t

    def at(self, seconds):
        self.t = Decimal(str(seconds))


def limiter_with(plan="FREE", client="c1"):
    clock = FakeClock()
    limiter = RateLimiter(clock)
    limiter.register(client, plan)
    return clock, limiter
