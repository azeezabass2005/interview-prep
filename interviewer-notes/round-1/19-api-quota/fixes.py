FIXES = [
    ("quota.py", "            bucket.tokens = bucket.tokens + elapsed * plan.refill_per_second",
     "            bucket.tokens = min(plan.capacity, bucket.tokens + elapsed * plan.refill_per_second)"),
    ("quota.py", "        bucket.tokens -= cost\n        if bucket.tokens < 0:\n            return 429",
     "        if bucket.tokens < cost:\n            return 429\n        bucket.tokens -= cost"),
    ("quota.py", "        return self.usage.get(key, 0)", "        return self.usage.get((key, month), 0)"),
    ("quota.py", "        self.usage[key] = used + cost", "        self.usage[(key, month)] = used + cost"),
    ("quota.py", "        if plan.hard_limit and used > plan.monthly_units:", "        if plan.hard_limit and used + cost > plan.monthly_units:"),
    ("quota.py", "        overage = used if used > plan.monthly_units else 0", "        overage = max(0, used - plan.monthly_units)"),
]
