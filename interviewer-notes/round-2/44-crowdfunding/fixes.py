FIXES = [
    ("crowd/services/pledges.py", "if limit is not None and self.claimed(c, tier) > limit:", "if limit is not None and self.claimed(c, tier) >= limit:"),
    ("crowd/services/pledges.py", "        p.amount = self._validate(c, tier, amount)\n",
     "        amount = self._validate(c, tier, amount)\n"
     "        limit = c.tiers[tier].limit\n"
     "        if tier != p.tier and limit is not None and self.claimed(c, tier) >= limit:\n"
     "            raise Rejected(f\"{tier} is sold out\")\n"
     "        p.amount = amount\n"),
    ("crowd/services/settlement.py", "        pledges = list(c.pledges.values())", "        pledges = [p for p in c.pledges.values() if p.status == ACTIVE]"),
    ("crowd/services/settlement.py", "        funded = total > c.goal", "        funded = total >= c.goal"),
    ("crowd/services/settlement.py",
     "            attempted = 0\n            for p in sorted(pledges, key=lambda p: p.pledge_id):\n                attempted += 1\n",
     "            successful = 0\n            for p in sorted(pledges, key=lambda p: p.pledge_id):\n"),
    ("crowd/services/settlement.py", "                    result[\"collected\"] += p.amount\n",
     "                    result[\"collected\"] += p.amount\n                    successful += 1\n"),
    ("crowd/services/settlement.py", "PER_CHARGE_FEE * attempted)", "PER_CHARGE_FEE * successful)"),
]
