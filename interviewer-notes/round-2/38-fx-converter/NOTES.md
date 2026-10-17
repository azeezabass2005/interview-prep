# R2-38 · FX Payments Service: Interviewer Guide

~220 lines in `fx/`. One passing test (EUR → USD, which hides the inversion, tier and rounding bugs). Quote → book is a small lifecycle
with time-based rules, so a controllable clock is essential.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Spread tier base | USD equivalent of the **source** amount at mid. |
| Quote expiry exactly at 30 s | Still valid; 30.001 s is expired. |
| Daily limit day | UTC calendar day of the booking. |
| Limit check uses which amount? | The quote's USD equivalent (mid, before spread). |
| Booking a quote twice | Rejected (already). |
| Rates against non-USD pairs | Not supported (rejected at publish). |

## Code map
| Module | Responsibility |
|---|---|
| `services/rates.py` | Publish rates, USD per unit, staleness |
| `services/quotes.py` | Spread tiers, cross mid, target rounding |
| `services/payments.py` | Booking, daily limit, cancellation |
| `store.py`, `api.py`, `app.py` | Storage, facade, wiring |

## Planted bugs (5)

### B1 · USD-base pairs not inverted
- **Where:** `rates.py::usd_per_unit`: returns `rate` for `USDJPY`; 1 JPY should be 1/151.20 USD.
- **Test:** 1,512 JPY → USD = **9.90**. The spec example (EUR → JPY) also needs it.
- **Fix:** `return rate if base == currency else 1 / rate`.

### B2 · Spread tier chosen on the source amount
- **Where:** `quotes.py::quote`: `spread_for(amount)` though `usd_equivalent` is computed on the line above.
- **Test:** 9,000 GBP (= $11,430) → 0.5% → **11,372.85** USD.
- **Fix:** `spread_for(usd_equivalent)`.

### B3 · Target amount rounded half-up
- **Where:** `quotes.py::quote`: `ROUND_HALF_UP`.
- **Test:** 100 EUR → USD: 107.415 → **107.41**.
- **Fix:** `ROUND_DOWN`.

### B4 · Expired quotes can be booked
- **Where:** `payments.py::book`: `QUOTE_TTL` is imported but never checked.
- **Test:** quote, advance 31 s, book → 409.
- **Fix:** `if now - quote.created_at > QUOTE_TTL: raise Rejected`.

### B5 · Cancelled payments still use the daily limit
- **Where:** `payments.py::booked_today`: doesn't filter `status == BOOKED`.
- **Test:** book $40,000, cancel it, book another $40,000 → allowed.
- **Fix:** skip cancelled payments.

Hints: (1) the spec sentence; (2) "which constant/variable is computed but unused?" (B2, B4).

## Red herrings
- JPY minor unit 0 is configured correctly.
- The staleness check in `usd_per_unit` is correct.

## Questions about the candidate's fixes (data structures)
- **B1:** "`usd_per_unit` scans all pairs per lookup. Better structure?" (Normalise at publish time into `dict currency → (usd_per_unit, at)`: O(1) lookups, and inversion happens once, in one place.)
- **B5:** "`booked_today` scans a customer's whole payment history on every booking. Alternative?" (A running total per (customer, day), decremented on cancel. Or keep payments sorted by time and only scan today's.) "What about two bookings at once on two servers?" (Check-then-act race on the limit: needs an atomic conditional update in a shared store.)
- **General:** "Why Decimal for rates, and how many decimal places should a cross rate keep?" (Decimal for exact, deterministic rounding; keep full precision until the final rounding.)

## Feature requests
1. **"Rate locks for corporates: a quote valid for 24 hours at a 0.10% premium."** Strong answer: TTL becomes part of the quote; the premium is added to the spread; exposure risk (stale rate for 24 h) needs a limit.
2. **"Fee schedule: $3 flat fee for payments under $1,000 USD-equivalent, deducted from the source amount."** Strong answer: order of operations (fee before conversion); rounding; how it shows on the quote.
3. **"Multi-leg payments: one source amount split across 3 recipients in different currencies."** Strong answer: one quote per leg vs a basket quote; all-or-nothing booking; the limit applies to the total.

## Scoring signals
- **Strong:** tests a USD-base currency (JPY) immediately; spots `QUOTE_TTL` unused; uses a fake clock for expiry and the daily limit.
- **Weak:** only EUR/USD quotes.
