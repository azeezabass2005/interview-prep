FIXES = [
    ("crowd.py", "        if c.pledges.pop(backer, None) is None:\n            raise CrowdError(\"no pledge to cancel\")",
     "        old = c.pledges.pop(backer, None)\n        if old is None:\n            raise CrowdError(\"no pledge to cancel\")\n        if old.tier:\n            c.tiers[old.tier].taken -= 1"),
    ("crowd.py", "        if tier != old.tier:\n            self._claim(c, tier, amount)",
     "        if tier != old.tier:\n            self._claim(c, tier, amount)\n            if old.tier:\n                c.tiers[old.tier].taken -= 1"),
    ("crowd.py", "        if self.total(campaign_id) <= c.goal:", "        if self.total(campaign_id) < c.goal:"),
    ("crowd.py", "        if at > c.deadline:", "        if at >= c.deadline:"),
    ("crowd.py", "                processing += money(p.amount * PROCESSING_PCT)", "                processing += money(p.amount * PROCESSING_PCT) + PROCESSING_FIXED"),
    ("crowd.py", "        processing += PROCESSING_FIXED * len(c.pledges)\n", ""),
    ("crowd.py", "            if self.gateway.charge(p.backer, p.amount):",
     "            if self.gateway.charge(p.backer, p.amount) or self.gateway.charge(p.backer, p.amount):"),
]
