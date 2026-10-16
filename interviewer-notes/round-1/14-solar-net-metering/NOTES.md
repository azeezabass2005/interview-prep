# R1-14 · Solar Net-Metering Billing: Interviewer Guide

~220 lines in `utility/`. One passing test (a simple 30-day bill, asserting only billable kWh). State carries across bills (registers, the bank),
so the candidate needs multi-reading scenarios.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Can a register roll over twice in a period? | No (physically impossible at household loads). |
| Tier proration rounding | Down to whole kWh: 15 days → tier 1 = 250 kWh. |
| Bank used and banked in the same period | Impossible: net is either positive or negative. |
| True-up timing | The bill whose **end** date is in December. A period ending 2 Jan doesn't qualify. |
| True-up after this bill's own banking | Yes: pay out what's in the bank after this bill is applied. |
| Out-of-order readings | Rejected (already). |

## Code map
| Module | Responsibility |
|---|---|
| `services/meters.py` | Register deltas |
| `services/tariff.py` | Tier sizes and energy charge |
| `services/billing.py` | Period maths, banking, charges, true-up |
| `reporting.py` | Annual statement (correct) |
| `store.py`, `api.py`, `app.py` | Storage, facade, wiring |

## Planted bugs (5)

### B1 · Register rollover ignored
- **Where:** `meters.py::register_delta`: returns `current − previous` (negative after a rollover).
- **Test:** import 99,900 → 300 → **400 kWh** imported.
- **Fix:** `(current - previous) % REGISTER_MAX`.
- **Hints:** (1) "What does the spec say about 5-digit registers?" (2) "Read 99,900, then 300."

### B2 · Tiers not scaled to the period length
- **Where:** `tariff.py::tier_sizes`: ignores `days`.
- **Test:** 15-day period, 400 kWh → 250 × 0.12 + 150 × 0.15 = **$52.50** energy (buggy $48.00).
- **Fix:** `size * days // 30`.
- **Hints:** "Bill a short period."

### B3 · Banked kWh are never used up
- **Where:** `billing.py::read`: computes `used` but never subtracts it from `account.bank_kwh`.
- **Test:** surplus 150 → next month 400 net bills 250 → the month after, 300 net bills **300** (buggy 150).
- **Fix:** `account.bank_kwh -= used`.
- **Hints:** "Check the bank after it's been used."

### B4 · Service charge is taxed
- **Where:** `billing.py::read`: `(energy + service) × 5%`.
- **Test:** the spec example → **$90.75** (buggy $91.35).
- **Fix:** `energy × TAX_RATE`.

### B5 · True-up keyed on the period start
- **Where:** `billing.py::read`: `previous.read_on.month` instead of `reading.read_on.month`.
- **Test:** period Nov 15 → Dec 15 with 200 kWh banked → payout **$8.00**, bank 0.
- **Fix:** use the new reading's month.

## Red herrings
- Register range validation: correct.
- Rounding each component with `cents`: per spec.

## Questions about the candidate's fixes (data structures)
- **B1:** "Why is modulo the right abstraction for rollover? What would break if a meter could roll over twice?" (You can't detect it from two readings; you'd need a max-plausible-usage check.)
- **B3:** "The bank is one integer per account. When would you need a ledger of bank movements instead?" (Audits, disputes, re-billing corrected readings: an append-only ledger lets you replay.)
- **Readings:** "`readings` is an append-only list; bills only need the last one. Memory over 20 years? Alternatives?" (Keep the last reading in the account and archive the rest.)
- **Reporting:** "The annual statement scans all bills: O(bills). Index by year?" (A dict year → bills, or bills sorted by end date + bisect.)

## Feature requests
1. **"Estimated reads: if a reading is missing, bill using the average daily usage of the last 3 bills, then true it up at the next actual read."** Strong answer: an estimated flag on the bill; the next actual reading bills the difference (actual delta − estimated usage); never negative billing without a credit line.
2. **"Time-of-use pricing: peak 16:00–21:00 at $0.30, off-peak $0.10, from smart meter interval data."** Strong answer: interval data model (15-minute buckets); banking per period type (ask PM); tier logic replaced.
3. **"Corrected reading: an earlier reading was mistyped; re-bill all affected periods."** Strong answer: bills are derived from readings; recompute from the corrected point forward, including the bank; issue adjustment bills instead of editing old ones.

## Scoring signals
- **Strong:** writes a reusable helper `bill_sequence([...readings])`; tests rollover, short periods, the bank across 3 periods and December.
- **Weak:** only single-period bills.
