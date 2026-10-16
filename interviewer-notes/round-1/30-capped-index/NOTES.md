# R1-30 · Capped Index Rebalance: Interviewer Guide

~170 lines in `indexing/`. One passing test (two equal constituents). Squarely in Bloomberg Index Services' domain: eligibility screens,
float adjustment, iterative capping, published weights, turnover.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Exactly 15% float / exactly 90 days | Eligible ("at least"). |
| Exactly at the cap | Allowed. |
| Proportional to what | Current weights of uncapped constituents. |
| Infeasible cap (n × cap < 1) | Error (already handled). |
| Residue recipient | Largest uncapped, ties alphabetical. |
| Turnover units | Percent, one-way. |

## Code map
| Module | Responsibility |
|---|---|
| `services/eligibility.py` | Screens |
| `services/weighting.py` | Float cap, raw weights, capping, publishing |
| `services/rebalance.py` | Orchestration, history, turnover |
| `store.py`, `api.py`, `app.py` | Storage, facade, wiring |

## Planted bugs (5)

### B1 · Capping is a single pass
- **Where:** `weighting.py::apply_cap`.
- **Test:** the spec example (cap 25%) → A/B/C 25.0000, D 16.6667, E 8.3333 (needs B2 fixed too).
- **Fix:** loop until no constituent exceeds the cap, tracking which are already capped.

### B2 · Excess split equally
- **Where:** `weighting.py::apply_cap`: `excess / len(under)`.
- **Test:** cap 30%, sizes 40/24/24/12 → **30/28/28/14** (one pass suffices here, so this isolates B2).
- **Fix:** `excess × w / Σ uncapped w`.

### B3 · 15% float excluded
- **Where:** `eligibility.py`: `free_float > MIN_FREE_FLOAT`.
- **Test:** a security with exactly 15% float is included.

### B4 · Float ignored in the cap
- **Where:** `weighting.py::float_cap`: `shares × price`.
- **Test:** equal size, float 1.0 vs 0.5, cap 100% → **66.6667 / 33.3333**.

### B5 · Exactly 90 days of seasoning excluded
- **Where:** `eligibility.py`: `days > 90`.
- **Test:** listed exactly 90 days before the rebalance → included.

Hints: (1) the spec sentence; (2) "turn the example into a test, then find which part fails".

## Red herrings
- Residue to the largest uncapped constituent: correct.
- Turnover formula: correct.
- The infeasible-cap guard: correct.

## Questions about the candidate's fixes (data structures)
- **B1:** "Your loop is O(k·n) where k = number of capping rounds (≤ n). Can you do better?" (Sort by weight descending once; walk from the top deciding capped vs uncapped with a running remainder: O(n log n). Nice, but the loop is clearer for n in the hundreds.) "Prove termination." (Each round caps at least one more constituent.)
- **Publishing:** "Why add the residue to one name rather than distribute by largest remainder?" (Spec choice; discuss fairness vs simplicity.)
- **History:** "History is a list of dicts per index. Turnover needs only the last one. Storage for 20 years of monthly rebalances?" (Tiny; but for daily ones consider storing only changes.)
- **Eligibility:** "The universe scan is O(U) per rebalance. Would you index by anything?" (No: a full screen per rebalance is natural; precompute float caps once.)

## Feature requests
1. **"Sector cap: no sector above 30%, then single-name cap 10%."** Strong answer: two nested constraints; iterate until both hold (or a constrained optimisation); order matters; tests where the sector cap binds.
2. **"Buffer rule: an existing constituent stays eligible unless its cap falls below $400M (not $500M)."** Strong answer: eligibility depends on previous membership; pass the previous constituents in; tests for both new and existing names.
3. **"Index level continuity: compute a new divisor so the index level doesn't jump at rebalance."** Strong answer: divisor = new total float-adjusted value / previous level; store the level history; corporate actions also adjust the divisor.

## Scoring signals
- **Strong:** separates the two capping bugs with different tests; probes every "at least".
- **Weak:** only the spec example, and can't explain why it fails.
