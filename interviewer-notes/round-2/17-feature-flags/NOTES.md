# R2-17 · Feature Flags: interviewer notes

~310 lines (small and dense). Good for a candidate who wants a smaller surface. The determinism ticket has a classic Python trap.

## Ticket map

| Ticket | Real root cause | Where | Trap |
|---|---|---|---|
| FF-1701 flickering | `bucket()` returns `random.randrange(100)` on every call | `services/bucketing.py` | **Python's built-in `hash()` is salted per process** (`PYTHONHASHSEED`), so `hash(user) % 100` is sticky within a process but differs across instances and restarts. Correct: a stable digest (`hashlib.sha256(f"{flag}:{user}")`) mod 100. Including the flag key matters: otherwise the same 20% of users get *every* experiment |
| FF-1702 override ignored | Evaluator checks segment rules **before** user overrides | `services/evaluator.py::is_enabled` | Fixing only for `False` overrides |
| FF-1703 change not visible | `FlagAdmin` writes to the DB but never calls `cache.invalidate()` on its own instance | `services/admin.py` | **AC says set the TTL to 0.** That makes every evaluation a DB query (thousands per second) and isn't needed: the README requires immediacy only on the writing instance. Invalidate locally; others converge within 30 s |
| FF-1704 archived flag on | `archived` is loaded but never checked | `services/evaluator.py::is_enabled` | Returning `False` instead of the caller's `default` |

## FF-1701 in depth
**Invariant:** `bucket(flag, user)` is a pure function of its inputs, stable across processes, deploys and Python versions.
Tests to look for: the same user evaluated many times on two instances gives one answer; the distribution over 10,000 users is about 20%; and
(the strongest) the value is identical in a **subprocess with a different `PYTHONHASHSEED`**. Candidates who know about hash randomisation
earn real credit here.

## FF-1703 in depth
Ask: "What's the cost of TTL 0?" Then: "What does the README actually require?" Accept: invalidate on write (same instance). Bonus: mention
a version number or pub/sub for faster cross-instance propagation (out of scope).

## Out-of-scope smells
- `load_all` filters overrides and rules per flag in Python (O(flags × rows)). Fine at this size.
- The admin API has no authorisation (out of scope).

## Strong prompts
- "Is `bucket()` deterministic? Would it be if we used `hash()`? Prove it with a test that runs a second interpreter."
- "List the evaluation steps in `is_enabled` in order and compare them with the README's order."
