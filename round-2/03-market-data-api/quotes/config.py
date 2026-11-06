# How long a latest-quote snapshot may be served from cache. Tickstream bills per request, and our contract allows 2 s staleness.
QUOTE_TTL_MS = 2_000
# FX rates move slowly enough to cache for a minute.
FX_TTL_SECONDS = 60
# Requests per minute, per customer, by plan.
PLAN_LIMITS = {"basic": 60, "pro": 600}
MAX_BATCH = 50
MAX_HISTORY_DAYS = 366
