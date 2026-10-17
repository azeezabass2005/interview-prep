# R1-47 · Feature Flags: Interviewer Guide

The Round 1 version of Round 2 #17. One file, `flags.py` (~80 lines), with one passing test. The spec example
passes on the buggy code (Ana is allowlisted; Ben's bucket is almost surely not 0).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Prerequisite flag unknown | Treated as off. |
| Cycles in prerequisites | Out of scope (would be a validation error). |
| Country `None` | Skip country targeting. |
| Bucket stability across deploys | Must be stable (pure function of key and user). |
| 100% rollout | Everyone (bucket ≤ 99 < 100). |

## Code map
`bucket` · `define` · `is_on` (the six steps).

## Planted bugs (5)

### B1 · Allowlist checked before denylist
- **Where:** `is_on` order.
- **Test:** user on both → **off**.

### B2 · Bucket ignores the flag key
- **Where:** `bucket` hashes only the user (parameter unused: clue).
- **Test:** compare with the spec's formula for `new-chart:ana`.

### B3 · 0% isn't nobody
- **Where:** `bucket(...) <= percentage`.
- **Test:** 1,000 users at 0% → **none** on.

### B4 · Country match is case-sensitive
- **Where:** `is_on`.
- **Test:** targeting `GB`, user country `gb` → **on**.

### B5 · Prerequisites ignored
- **Where:** `is_on`; `prerequisites` never read (clue).
- **Test:** prerequisite disabled → **off** even for an allowlisted user.

Hints: (1) "the spec's list is an order — test the conflicts between steps"; (2) "which fields/parameters are never used?"

## Red herrings
- Percentage validation: correct.
- Unknown flag → off: correct.

## Questions about the candidate's fixes (data structures)
- **B2:** "Why does including the flag key matter?" (Otherwise the same 10% of users get every experiment: correlated exposure, biased results.)
- **Hashing:** "Why sha256 and not Python's `hash()`?" (`hash()` is salted per process — not stable across runs/servers.)
- **Sets for allow/deny lists:** "Why sets?" (O(1) membership.) "A 1M-user allowlist?" (Bloom filter in memory + exact check elsewhere, or segment ids.)
- **B5 recursion:** "Prerequisites call `is_on` recursively. Risks and mitigations?" (Cycles → infinite recursion: validate the graph as a DAG at define time — topological sort.)

## Feature requests
1. **"Multivariate flags (A/B/C with 50/30/20)."** Strong answer: bucket ranges per variant; sticky assignment; percentages add to 100.
2. **"Scheduled rollout: 10% → 50% → 100% over a week."** Strong answer: percentage as a function of time; monotonic so users never flip off.
3. **"Audit log of flag changes."** Strong answer: append-only events with who/when/what; ability to roll back.

## Scoring signals
- **Strong:** tests conflicts between rules; validates the hash formula against the spec; thinks about 0%/100% edges.
- **Weak:** only allowlist and disabled tests.
