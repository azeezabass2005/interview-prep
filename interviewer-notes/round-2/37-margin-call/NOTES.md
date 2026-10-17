# R2-37 · Prime Brokerage Margin Engine: Interviewer Guide

~285 lines in `margin/`. One passing test (a well-collateralised account). The spec's example **passes** on the buggy code; every
bug needs an extra ingredient (shorts, staleness, an odd shortfall, deposit timing).

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Concentration denominator | Gross **long** MV only. |
| Exactly 40% | Not concentrated. |
| Stale = ? | Price date earlier than run date − 1 day (a price from yesterday is fine). |
| Order: concentration then staleness | Concentration first (max with 50%), then +10 points. A concentrated stale position is 60%. |
| Short requirement | 130% of |short MV| (principal + 30%). |
| Call rounding | Always up to the next $100. |
| Deposits before a call | Don't count toward meeting it (they're already in the excess). |
| Second run with an open call | Keep the existing call (don't issue another). |

## Code map
| Module | Responsibility |
|---|---|
| `services/prices.py` | Publish and look up prices (latest on/before date) |
| `services/valuation.py` | Lines, haircuts (concentration, staleness), collateral / requirement / excess |
| `services/calls.py` | Call issuance, deposits, meeting calls |
| `services/liquidation.py` | Liquidation plan (correct) |
| `store.py`, `api.py`, `app.py` | Storage, facade, wiring |

## Planted bugs (5)

### B1 · Concentration measured against net MV
- **Where:** `valuation.py::lines`: `base` sums **all** lines including shorts.
- **Test:** longs A 30k, B 38k, C 32k (equities), short S 20k → B is 38% of gross long → 25% → collateral **75,000** (buggy 65,500).
- **Fix:** sum only `qty > 0`.

### B2 · Short requirement missing the principal
- **Where:** `valuation.py::summary`: `|MV| × 0.30`.
- **Test:** short 100 @ $100, no cash → requirement **13,000**.
- **Fix:** `× (1 + SHORT_ADD_ON)`.

### B3 · Call rounded to the nearest $100
- **Where:** `calls.py::round_call`: `ROUND_HALF_UP`.
- **Test:** the example with cash −$100,040 → call **$16,100** (buggy $16,000).
- **Fix:** `ROUND_CEILING`.

### B4 · Staleness surcharge swallowed by concentration
- **Where:** `valuation.py::lines`: the surcharge is added **before** `max(haircut, 50%)`.
- **Test:** the example with AAPL's last price two days old → 60% → collateral 76,000 → call **$24,000** (buggy $16,000).
- **Fix:** apply concentration first, then add the surcharge.

### B5 · Old deposits meet new calls
- **Where:** `calls.py::_check_met`: sums **all** deposits ever.
- **Test:** deposit $5,000, then a $16,000 call is issued, then deposit $12,000 → call still OPEN.
- **Fix:** only deposits with `on >= call.issued_on` (and made after it).

Hints for each: (1) the spec sentence; (2) "build an account where the two readings differ".

## Red herrings
- Liquidation ordering and per-share improvement: correct.
- `latest` picks the newest price on or before the run date: correct.

## Questions about the candidate's fixes (data structures)
- **Prices:** "`latest` filters every historical price per lookup: O(p). With years of daily prices?" (Keep prices sorted by date per symbol and `bisect_right`: O(log p). Or keep just the latest per symbol for the nightly run.)
- **B5:** "Deposits per account are a list; meeting a call sums a filter. Alternative?" (Track `deposited_since_call` on the call itself, incremented on deposit: O(1).)
- **Open call:** "`open_call` scans the account's call history. Better?" (Store the open call id on the account. Invariant: at most one open call, enforced in one place.)
- **Liquidation:** "Sorting longs is O(n log n). If you only need enough sales to cover the call?" (A heap and pop until covered: O(n + k log n).)

## Feature requests
1. **"Cross-margining: two accounts of the same client share collateral."** Strong answer: a client-level aggregation; concentration computed at client level; calls issued at client level; which account's positions to liquidate.
2. **"Intraday margin runs every hour with real-time prices."** Strong answer: incremental valuation on price ticks (only affected accounts: index accounts by symbol); call idempotency within a day.
3. **"Call deadline: an unmet call after 2 business days triggers automatic liquidation."** Strong answer: business-day calendar; a scheduler; partial cures reduce the liquidation amount; audit trail of actions.

## Scoring signals
- **Strong:** notices the example passes, then adds one ingredient at a time; tests deposit timing; asks about rule order (concentration vs staleness).
- **Weak:** only long-only, fresh-price scenarios.
