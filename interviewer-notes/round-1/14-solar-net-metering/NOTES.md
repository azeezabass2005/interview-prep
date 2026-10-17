# R1-14 · Solar Net Metering: Interviewer Guide

One file, `netmeter.py` (~95 lines), with one passing test (a 30-day month without solar). The spec example passes on the buggy code.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Rounding of the prorated tier | Nearest whole kWh (250 for 15 days). |
| Bank larger than net | Use only what's needed; the rest stays. |
| Can the bill go below $10? | No; credit is kWh, not money. |
| Rollover twice in one period | Impossible (would be > 100,000 kWh). |
| True-up of an empty bank | $0.00. |

## Code map
`_usage` · `read` (baseline, validation) · `_bill` (net, bank, tiers) · `true_up`.

## Planted bugs (5)

### B1 · Register rollover
- **Where:** `_usage`; `ROLLOVER` is used only for validation.
- **Test:** 99,900 → 100 → 200 kWh → **$40.00**.

### B2 · Tier not prorated
- **Where:** `_bill`: `threshold = TIER_KWH`; `days` and `TIER_DAYS` unused (clue).
- **Test:** 15 days, 400 kWh → 250 × 0.15 + 150 × 0.20 + 10 = **$77.50** (buggy $70.00).

### B3 · Bank never decreases
- **Where:** `_bill`: computes `banked_used` but doesn't subtract it.
- **Test:** bank 100; use 60, then 60 more → second bill charges 20 kWh → **$13.00** (buggy $10.00).

### B4 · True-up doesn't reset the bank
- **Where:** `true_up`.
- **Test:** after a true-up the bank is 0.

### B5 · Banks all exports, not the excess
- **Where:** `_bill`: `bank += exported`.
- **Test:** import 300, export 500 → bank **200** (buggy 500).

Hints: (1) "which inputs does `_bill` receive and never use?"; (2) "run three months in a row".

## Red herrings
- Readings must move forward: correct.
- Rounding the energy charge once: correct.

## Questions about the candidate's fixes (data structures)
- **B1:** "Why does `% ROLLOVER` work for both normal and rolled cases?" (Modular arithmetic; fails if usage ≥ 100,000 in one period.)
- **Bills list:** "Find a customer's last 12 bills: O(all bills). Better?" (Per-customer list or deque(maxlen=12).)
- **Bank as int kWh.** "If credits had to expire after 12 months, what would you store?" (FIFO lots with dates in a deque; consume oldest first.)
- **Accounts via `setdefault`.** "What's the risk?" (A typo creates a new customer silently; explicit registration is safer.)

## Feature requests
1. **"Time-of-use rates: peak (16:00–21:00) vs off-peak."** Strong answer: interval data or separate registers; bank valued per period; rates as data.
2. **"Bank credits expire after 12 months."** Strong answer: dated lots (deque), FIFO consumption, expiry on each bill.
3. **"Estimated reading when the meter can't be read."** Strong answer: estimate from history; mark as estimated; correct on the next actual reading.

## Scoring signals
- **Strong:** chains several readings; notices the unused `days`; asks about rollover.
- **Weak:** single-period tests only.
