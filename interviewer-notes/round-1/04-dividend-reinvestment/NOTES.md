# R1-04 · Dividend Reinvestment (DRIP): Interviewer Guide

~320 lines in `drip/`. One passing test (US cash holder). Two of the bugs are **"as of which date?"** bugs (point-in-time state), a very
common class in financial systems. The others are a default value, a missing carry-over and a wrong base for a cap.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Record date inclusive? | Yes, movements dated on the record date count. |
| Enrolment change effective on the record date itself? | Counts (effective from that day). |
| Country codes case? | Case-insensitive ISO codes. Unknown → 30%. |
| Order of steps | gross → withholding (on gross) → fee (capped at 5% of **net**) → add leftover → buy. |
| Leftover scope | Per account **and** security. |
| Negative holdings | Not possible in practice; skip ≤ 0 (as coded). |
| Same pay date for two events of one security | Out of scope. |
| Reinvested shares count for the next event? | Yes, from their pay date onward. |

## Code map
| Module | Responsibility |
|---|---|
| `register.py` | Point-in-time holdings from movements |
| `services/enrolment.py` | Enrolment history (`enrolled_on` is correct and **unused**: a clue) |
| `services/withholding.py` | Rates by residence |
| `services/processor.py` | Entitlement, cash/reinvest decision, reinvestment maths |
| `services/reports.py` | Tax report and event totals (correct) |
| `store.py`, `api.py`, `app.py` | Storage, facade, wiring |

## Planted bugs (5)

### B1 · Entitlement measured on the pay date
- **Where:** `processor.py::process`: `holdings(event.security, event.pay_date)`.
- **Test:** 100 shares before the record date + 50 bought between record and pay date → paid on 100 (gross $82.00, buggy $123.00).
- **Fix:** `event.record_date`.
- **Hints:** (1) "Trade between the record date and the pay date." (2) "Which date is passed to `holdings`?"

### B2 · Unknown countries withheld at 0%
- **Where:** `withholding.py::withholding_rate`: `.get(country, Decimal("0"))`. `DEFAULT_WITHHOLDING_RATE` exists and is unused.
- **Test:** a Brazilian resident (BR), 100 shares → withholding $24.60.
- **Fix:** default to `DEFAULT_WITHHOLDING_RATE`.
- **Hints:** "Test a country that isn't in the table."

### B3 · Enrolment read "now", not on the record date
- **Where:** `processor.py::process`: `currently_enrolled(...)`. `enrolled_on(account, security, date)` already exists.
- **Test:** enrol with effective date after the record date → this event pays cash. And un-enrolling after the record date still reinvests.
- **Fix:** `self._enrolment.enrolled_on(account_id, event.security, event.record_date)`.
- **Hints:** "Change enrolment between record date and processing."

### B4 · Leftover cash never reused
- **Where:** `processor.py::_reinvest`: the leftover is stored but never added to the investable cash.
- **Test:** US, enrolled, 10 shares, two quarterly events at $0.82 / $40: Q2 buys **0.1983** shares and leaves 0 (buggy 0.1982).
- **Fix:** `investable = net - fee + self._store.leftover(account_id, security)`.
- **Hints:** "Run two events in a row for a small holder." "Where is `leftover` read?"

### B5 · Fee cap uses gross instead of net
- **Where:** `processor.py::_reinvest`: `gross * FEE_CAP_RATE`.
- **Test:** GB resident (15%), enrolled, 10 shares: gross 8.20, tax 1.23, net 6.97 → fee **0.35** (buggy 0.41).
- **Fix:** `net * FEE_CAP_RATE`.
- **Hints:** "Combine withholding and a small reinvestment."

## Red herrings
- `ROUND_DOWN` on gross and on shares, and `ROUND_HALF_UP` on tax and fee, are all by spec.
- Skipping accounts with zero shares is correct.

## Questions about the candidate's fixes (data structures)
- **B1:** "`holdings()` scans every movement of the security on each call: O(M). For 1M shareholders and many events, how would you make 'holding on date D' fast?" (Per (account, security) a list of movements sorted by date with running totals → `bisect` = O(log m). Or nightly snapshots + deltas. Trade-off: memory vs query time.)
- **B3:** "Enrolment history is a sorted list scanned linearly. Better?" (`bisect_right` on effective dates → O(log k). Note `add_enrolment` re-sorts on every insert: O(k log k); `insort` makes it O(k).) "What happens with two changes effective the same day?" (Ambiguous: last write wins; ask PM.)
- **B4:** "Leftovers live in a dict keyed by (account, security). Why a tuple key rather than nested dicts?" (Simpler, O(1); nested dicts help when you need all securities of an account.) "What happens to the leftover if the process crashes after buying shares but before saving it?" (Lost or doubled: persist both atomically.)
- **General:** "Why Decimal? Show me a float that breaks this." (0.1 + 0.2; and fractional shares to 4 dp.)

## Feature requests
1. **"Partial DRIP: shareholders can reinvest a percentage (e.g. 60%) and take the rest as cash."**
   Strong answer: the enrolment model gains a percentage (history keeps working); the split happens after withholding; how rounding is shared (cash rounded down, rest reinvested); the fee applies only to the reinvested part.
2. **"Scrip dividend: the company issues new shares at a 3% discount to the market price instead of buying in the market."**
   Strong answer: the reinvestment price comes from the event; the discount is a policy on the event; reporting of newly issued shares vs market purchases.
3. **"Re-process an event after a late-reported trade (before the record date)."**
   Strong answer: processing must be idempotent; compute the delta payment; reverse/re-issue DRIP movements; audit trail; never edit history in place.

## Scoring signals
- **Strong:** asks "as of when?" for every input (holdings, enrolment, leftover), notices `enrolled_on` and `DEFAULT_WITHHOLDING_RATE` are unused, builds a two-event test.
- **Weak:** tests only the single-event happy path; "fixes" the rounding modes (red herring).
