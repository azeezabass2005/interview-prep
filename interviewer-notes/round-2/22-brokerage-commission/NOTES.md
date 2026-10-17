# R2-22 · Brokerage Fee Engine: Interviewer Guide

~325 lines in `fees/`. One passing test (a small equity buy). Bugs span the commission rules, rounding, statement windowing and the
volume-discount counter. The spec's examples are mostly untested.

## Session plan (60 min)
| Time | What happens |
|---|---|
| 0–5 | Resume + one past problem |
| 5–15 | Spec summary + clarifying questions |
| 15–20 | Code map with the agent |
| 20–45 | Bug hunt (expect 3–5) |
| 45–55 | Data-structure questions on fixes + a feature request |
| 55–60 | Remaining risks |

## PM answers
| Question | Answer |
|---|---|
| Marginal or flat tiers? | Marginal, like tax brackets (the $60k → $32 example). |
| Band edges | $10,000 exactly is all in band 1; $50,000 exactly is bands 1–2 only. |
| Discount base | 20% of the commission **after** min/max. Never applies to the reg fee. |
| Ties in execution time | Order by trade id. |
| Does a busted trade's number get reused? | Busted trades don't exist for counting. The next active trade takes the number. |
| Time zone of executed_at | Exchange local time, naive. No conversion. |
| Option minimum | $1.00, and no maximum ($0.65 × 1,000 contracts = $650). |
| Reg fee on options | Yes, on sells, using contracts × price × 100. |

## Code map
| Module | Responsibility |
|---|---|
| `api.py`, `app.py` | Facade and wiring |
| `services/trades.py` | Record / bust trades, validation (correct) |
| `services/commission.py` | Notional, equity tiers, option per-contract |
| `services/regulatory.py` | SEC-style fee |
| `services/statements.py` | Month window, ordering, numbering, discount |
| `money.py` | Rounding helpers: `half_up`, `always_up` (note: `always_up` is unused, a clue) |
| `reporting.py` | Revenue summary (correct, built on statements) |

## Planted bugs (5)

### B1 · Equity tiers are flat, not marginal
- **Where:** `services/commission.py::tiered_equity_commission`. It returns `amount × rate` of the band the whole amount falls in.
- **Test:** $60,000 → $32.00 (buggy $12.00). Also $10,000 → $10.00 (boundary).
- **Fix:** accumulate `(min(amount, upper) - lower) × rate` per band.
- **Hints:** (1) "Turn the spec's first example into a test." (2) "How much of a $60k trade is charged 0.10%?"

### B2 · Regulatory fee rounds half-up, not always up
- **Where:** `services/regulatory.py`. It uses `half_up`; `money.always_up` exists and is unused.
- **Why it hides:** the spec's example (0.139) rounds to 0.14 either way.
- **Test:** sell notional $12,000 → 0.3336 → **$0.34** (buggy $0.33).
- **Fix:** `always_up`.
- **Hints:** (1) "Does the spec example distinguish the two rounding modes?" (2) "Which helpers in money.py are unused?"

### B3 · Busted trades consume discount numbers
- **Where:** `services/statements.py::build`. `enumerate(...)` numbers every trade in the month, then busted ones are skipped. The busted trade still advanced the counter.
- **Test:** 51 trades in March, one of the first 50 busted → the last trade is only the 50th active → no discount (buggy: 20% discount).
- **Fix:** filter busted trades **before** numbering.
- **Hints:** (1) "Bust a trade early in a busy month." (2) "What does the counter count?"

### B4 · Statement includes the 1st of next month
- **Where:** `services/statements.py::trades_in_month`. It uses `start <= date <= end`, where `end` is already the 1st of next month.
- **Test:** a trade at 2026-04-01 00:30 must not appear on the March statement (and must appear in April).
- **Fix:** `< end`.
- **Hints:** (1) "What's the spec's exact month window?" (2) "What does `month_bounds` return as `end`?"

### B5 · Options are capped at $50
- **Where:** `services/commission.py::option_commission`. It clamps with `EQUITY_MAX`.
- **Test:** 100 contracts → $65.00 (buggy $50.00). 1 contract → $1.00 (min).
- **Fix:** `clamp(..., OPTION_MIN)` with no high bound.
- **Hints:** (1) "Price a large option order." (2) "Which constants does `option_commission` use?"

## Red herrings
- `notional` for options multiplies by 100: correct.
- Discount computed after the clamp: correct per PM.
- Duplicate trade-id rejection: correct.

## Questions about the candidate's fixes (data structures)
- **B1:** "Your tier loop is O(T) per trade. Could you precompute anything?" (Cumulative charge at each band's upper bound, then binary search the band: O(log T). Overkill for 3 bands; say why.) "How would you make the tier table data-driven and validate it?" (Ascending bounds, last unbounded, rates non-negative.)
- **B3:** "You filtered then enumerated. Statement build sorts the month's trades: O(n log n). If statements were generated incrementally as trades arrive, how would you know a trade's month-number in O(1)?" (Per-(account, month) counter maintained on record **and** on bust. But a bust renumbers later trades. Discuss why recomputation on statement generation is simpler and safer.)
- **B4:** "Your store keeps a list of trade ids per account. Filtering a month is O(all trades ever). Alternative?" (Index by `(account, year-month)` → list; or keep per-account lists sorted by time and `bisect` the bounds: O(log n + k).)
- **General:** "Why Decimal and not float?" (0.0000278 × notional; exact cents and deterministic rounding modes.)

## Feature requests
1. **"Introduce a Pro plan: flat $4.95 per equity trade, options $0.50/contract, volume discount from the 31st trade."**
   Strong answer: plan stored on the account; a per-plan fee schedule object (strategy) rather than if/else in every function; existing tests become plan-parameterised; month-boundary plan changes need a rule (ask PM: plan at execution time).
2. **"Commission caps per account per day: never more than $200 per trading day in commission."**
   Strong answer: the cap applies after discounts; trades in time order; how to allocate the excess (the last trades get reduced); deterministic tests; the statement shows a "daily cap adjustment" line for auditability.
3. **"Re-issue statements when a trade is busted after its statement was sent."**
   Strong answer: statements are derived (rebuildable); store a version/hash of each issued statement; generate a correction (diff) rather than mutating history.

## Scoring signals
- **Strong:** writes the three spec examples as tests first (finds B1 immediately); notices `always_up` unused; tests month edges and busted trades deliberately.
- **Weak:** fixes rounding by switching to float; doesn't test options at scale.

## Model prompts
- "List every place commission is computed or adjusted, with file and function. Don't change code."
- "For the volume discount, show me exactly which trades are counted and in what order."
