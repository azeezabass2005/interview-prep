# 30 · Capped Index Weights: interviewer notes

Code: `index/weights.py`. Shape: eligibility thresholds, the correct measure (float-adjusted), **iterative** redistribution, proportional vs equal splitting, rounding residue for conservation.
Directly in Bloomberg Index Services' domain.

## PM answers

| Topic | Answer |
|---|---|
| Exactly 15% float | Eligible ("at least"). |
| Exactly at the cap | Allowed (no further capping). |
| Proportional to what? | Current weights of the uncapped constituents (equivalent to their float caps). |
| Cap infeasible (fewer than 1/cap constituents) | Out of scope. If asked: raise an error; with 3 names and a 10% cap it can't sum to 100%. |
| Residue recipient | Largest **uncapped** constituent after capping; ties alphabetical. |
| Ineligible securities | Not in the output at all. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `apply_cap` | Single pass. A constituent pushed over the cap by redistribution stays over | loop until no breach | spec example (25% cap): A/B/C 25, D 16.6667, E 8.3333 |
| B2 | `apply_cap` | Excess split **equally** | split in proportion to the uncapped weights | 30% cap, 40/24/24/12 → 30/28/28/14 |
| B3 | `is_eligible` | `free_float > 15%` excludes exactly 15% | `>=` | 15% float security is in the index |
| B4 | `float_adjusted_cap` | Ignores free float | `shares * free_float * price` | equal size, float 1.0 vs 0.5 → 66.6667 / 33.3333 |
| B5 | `publish` | Rounding residue dropped (3 × 33.3333 = 99.9999) | add the residue to the largest uncapped | three equal names sum to 100.0000 |

B1's hidden test also needs B2 fixed (the example's numbers are proportional). That's expected: the spec example exercises the whole algorithm.

**Red herring:** `total == 0 → {}` is fine.

## Follow-ups
- Prove the loop terminates. (Each iteration caps at least one more constituent; at most n iterations.)
- Complexity: O(n²) worst case; fine for index sizes (hundreds to low thousands).
- Why Decimal? (Published weights must reconcile exactly with clients' replication.)
