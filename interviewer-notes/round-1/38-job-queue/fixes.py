FIXES = [
    ("jobqueue.py", "key=lambda j: (-j.priority, j.seq))", "key=lambda j: (j.priority, j.seq))"),
    ("jobqueue.py", "        return job.status == \"PENDING\"",
     "        if job.status == \"LEASED\" and job.lease_until <= now:\n            job.status, job.worker, job.lease_until = \"PENDING\", None, None\n"
     "        return job.status == \"PENDING\" and job.run_at <= now"),
    ("jobqueue.py", "        if job.attempts >= job.max_attempts - 1:", "        if job.attempts >= job.max_attempts:"),
    ("jobqueue.py", "        if job is None or job.status != \"LEASED\":\n            raise QueueError(\"job is not leased\")",
     "        if job is None or job.status != \"LEASED\" or job.worker != worker or job.lease_until <= now:\n            raise QueueError(\"you do not hold this lease\")"),
]
