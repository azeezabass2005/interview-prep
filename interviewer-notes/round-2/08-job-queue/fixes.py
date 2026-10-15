FIXES = [
    ("jobq/services/worker.py", "        lease_until = job.claimed_at + timedelta(seconds=LEASE_SECONDS)",
     "        lease_until = self._clock.now() + timedelta(seconds=LEASE_SECONDS)"),
    ("jobq/services/worker.py", "        if attempts > job.max_attempts:", "        if attempts >= job.max_attempts:"),
    ("jobq/services/backoff.py", "    return BACKOFF_BASE_SECONDS * 2 * attempt",
     "    return min(BACKOFF_CAP_SECONDS, BACKOFF_BASE_SECONDS * 2 ** (attempt - 1))"),
    ("jobq/services/queue.py", "from datetime import datetime", "from datetime import datetime, timezone"),
    ("jobq/services/queue.py", "    return parsed.replace(tzinfo=None)", "    return parsed.astimezone(timezone.utc).replace(tzinfo=None)"),
]
