FIXES = [
    ("gateway/app.py", "from .counters import LocalCounterStore", "from .counters import DbCounterStore"),
    ("gateway/app.py", "from .repositories.keys import ApiKeyRepository",
     "from .repositories.counters import CounterRepository\nfrom .repositories.keys import ApiKeyRepository"),
    ("gateway/app.py", "    counters = LocalCounterStore()", "    counters = DbCounterStore(CounterRepository(db))"),
    ("gateway/limiter.py", "        count = self._counters.increment(user_id, window_start)",
     "        count = self._counters.increment(f\"{tenant_id}:{user_id}\", window_start)"),
    ("gateway/limiter.py", "        retry_after = max(1, int(now - window_start))",
     "        retry_after = max(1, math.ceil(window_start + WINDOW_SECONDS - now))"),
    ("gateway/limiter.py", "from dataclasses import dataclass", "import math\nfrom dataclasses import dataclass"),
    ("gateway/plans.py", "        if cached is None:", "        if cached is None or self._clock.time() - cached[1] >= self._ttl:"),
]
