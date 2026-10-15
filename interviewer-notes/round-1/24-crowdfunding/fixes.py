FIXES = [
    ("crowd/campaign.py", "        amount = Decimal(amount)\n",
     "        amount = Decimal(amount)\n        if self._clock.now() >= self.deadline:\n            raise PledgeRejected(\"campaign has ended\")\n"),
    ("crowd/campaign.py", "self._claimed(tier) > t.limit", "self._claimed(tier) >= t.limit"),
    ("crowd/campaign.py", "return sum((p.amount for p in self.pledges), ZERO)",
     "return sum((p.amount for p in self.pledges if not p.cancelled), ZERO)"),
    ("crowd/campaign.py",
     """        funded = total > self.goal
        active = [p for p in self.pledges if not p.cancelled]
        platform = cents(total * PLATFORM_RATE)
        processing = cents((total - platform) * PROCESSING_RATE + PER_PLEDGE_FEE * len(active))
""",
     """        funded = total >= self.goal
        active = [p for p in self.pledges if not p.cancelled]
        if not funded:
            return Outcome(False, total, ZERO, ZERO, ZERO, [])
        platform = cents(total * PLATFORM_RATE)
        processing = cents(total * PROCESSING_RATE + PER_PLEDGE_FEE * len(active))
"""),
]
