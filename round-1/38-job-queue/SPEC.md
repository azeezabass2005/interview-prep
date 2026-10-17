# Job Queue

Background work (sending e-mails, generating reports) goes through a job queue. Producers enqueue jobs; workers **lease** them, do the
work and report back. `jobqueue.py` is the queue.

## Jobs

A job has a name, a **priority** (1 = most urgent … 5 = least), a `run_at` time (default now; later for delayed jobs), and
`max_attempts` (default 3). An optional **unique key** prevents enqueueing a duplicate while a job with that key is still pending or leased.

## Leasing

- `lease(worker, now)` hands out the **most urgent ready job** (`run_at` ≤ now). Same priority → the one enqueued first.
- A lease lasts **30 seconds**. If the worker hasn't completed or failed the job by then, the lease **expires** and the job can be leased
  again by any worker.

## Finishing

- Only the worker **currently holding the lease** may complete or fail a job.
- `fail`: the attempt counts. If the job has attempts left it's retried after a **backoff of 10 s × 2^attempts so far** (20 s after the
  1st failure, 40 s after the 2nd). After `max_attempts` failed attempts it goes to **DEAD**.

## Example

Enqueue `send-email` (priority 3) and `fraud-check` (priority 1). A worker leases → gets **fraud-check**. It fails at 12:00:00 → retried
from **12:00:20**.
