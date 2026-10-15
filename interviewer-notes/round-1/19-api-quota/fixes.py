FIXES = [
    ("quota/bucket.py",
     "        elapsed = Decimal(int(max(now - self.last, Decimal(0))))\n"
     "        self.tokens = self.tokens + elapsed * self.plan.refill_per_second\n",
     "        elapsed = max(now - self.last, Decimal(0))\n"
     "        self.tokens = min(self.plan.capacity, self.tokens + elapsed * self.plan.refill_per_second)\n"),
    ("quota/bucket.py",
     "        missing = cost - self.tokens\n        wait = (missing / self.plan.capacity)",
     "        if cost > self.plan.capacity:\n            return Decision(False, None)\n"
     "        missing = cost - self.tokens\n        wait = (missing / self.plan.refill_per_second)"),
    ("quota/bucket.py", "        self._refill(now)\n        self.plan = plan\n",
     "        self._refill(now)\n        self.plan = plan\n        self.tokens = min(self.tokens, plan.capacity)\n"),
]
