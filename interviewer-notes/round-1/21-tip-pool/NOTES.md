# 21 · Restaurant Tip Pool: interviewer notes

Code: `tips/pool.py`. Shape: deductions on one input only, exclusion rules (role and threshold), aggregation across records, largest-remainder rounding.

## PM answers

| Topic | Answer |
|---|---|
| Fee rounding | Pool rounded half-up to the cent after the fee. |
| Exactly 2 hours | Eligible ("fewer than 2" are excluded). |
| Manager who also bussed | Manager hours give no weight; busser hours do. Total hours (including manager hours) count toward the 2 h minimum? **Only eligible-role hours count.** |
| Multiple roles | Sum points × hours per role. |
| Ties in remainder | Alphabetical by name. |
| Nobody eligible | Return an empty payout; the pool is held over (out of scope). |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `pool.py::pool_amount` | 3% fee taken from cash too | fee on card only | card 1,000 + cash 200 → 1,170.00 (buggy 1,164.00) |
| B2 | `pool.py::weights` | Managers kept (their weight is 0 but they still appear, and their hours count toward eligibility) | skip `INELIGIBLE_ROLES` | example: Dan not in payouts |
| B3 | `pool.py::weights` | `hours > MIN_HOURS` excludes exactly 2 h | `>=` | busser at exactly 2 h is paid |
| B4 | `pool.py::weights` | `weight[name] = ...` overwrites; multi-role weight lost | `+=` | Fay BUSSER 3 h + SERVER 3 h + Gus SERVER 3 h: Fay 45 vs Gus 30 → 60% / 40% |
| B5 | `pool.py::distribute` | Leftover cents go alphabetically, not by largest remainder | sort by `(-remainder, name)` | pool $1 (cash), weights A 1 / B 2 → A 0.33, B 0.67 |

**Red herring:** `ROLE_POINTS["MANAGER"] = 0` looks like it already excludes managers, but a zero-weight entry still shows up in the result (and in eligibility). Watch the agent claim "managers already get nothing" and see whether the candidate checks the actual output.

**Clue:** `INELIGIBLE_ROLES` is defined and never used.

## Follow-ups
- Why Decimal and why round down then distribute? (Conservation: sum == pool.)
- If tip pools get audited, what would you log? (Inputs, weights, exact shares, remainder allocation.)
