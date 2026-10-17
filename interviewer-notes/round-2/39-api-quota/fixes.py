FIXES = [
    ("metering/services/bucket.py",
     "    elapsed = Decimal(int(max(now - client.last_refill, Decimal(0))))\n    client.tokens = client.tokens + elapsed * client.plan.refill_per_second",
     "    elapsed = max(now - client.last_refill, Decimal(0))\n    client.tokens = min(client.plan.capacity, client.tokens + elapsed * client.plan.refill_per_second)"),
    ("metering/services/bucket.py", "(missing / client.plan.capacity)", "(missing / client.plan.refill_per_second)"),
    ("metering/services/limiter.py",
     "        meter.record(client, cost, now)\n        if client.tokens >= cost:\n            client.tokens -= cost\n",
     "        if client.tokens >= cost:\n            client.tokens -= cost\n            meter.record(client, cost, now)\n"),
    ("metering/services/invoices.py", "    overage_units = used if used > plan.allowance else 0", "    overage_units = max(used - plan.allowance, 0)"),
]
