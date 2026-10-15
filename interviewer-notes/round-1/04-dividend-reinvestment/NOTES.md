# 04 · Dividend Reinvestment (DRIP): interviewer notes

Code: `drip/`. Shape: snapshot at a date, ordered pipeline (gross → tax → fee → buy), rounding direction matters, residual rollover.

## PM answers

| Topic | Answer |
|---|---|
| Record date inclusive? | Yes: moves dated on the record date count. |
| Fee cap base | 5% of **net** (after withholding), not gross. |
| Order | gross → withholding (on gross) → fee (on net) → invest. |
| Rounding of shares | Truncate to 4 dp. Never round up. |
| Residual | Exact Decimal, kept per account, added to the *next* reinvestment's investable cash. |
| Does withholding apply to DRIP holders? | Yes, same as cash holders. |
| Negative/short positions | Skipped (no payment), as the code does. |
| Multiple symbols | One event at a time; ledger is single-symbol for this exercise. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `processor.py::process` | Uses `positions()` (today), not `positions_as_of(record_date)` | `positions_as_of(event.record_date)` | 100 sh at record, +50 after: cash holder paid on 100 (82.00), not 150 |
| B2 | `processor.py::_reinvest` | Withholding computed on `gross - fee` instead of gross | withhold on gross first | Non-resident DRIP 100 sh: withholding 12.30 (buggy: 12.23) |
| B3 | `processor.py::_reinvest` | Shares `ROUND_HALF_UP`, so it can spend cash it doesn't have (negative residual) | `ROUND_DOWN` | 10 sh example: 0.1947 shares (buggy: 0.1948, residual −0.002) |
| B4 | `processor.py::_reinvest` | Residual is stored but never added to the next reinvestment | `investable += self.residual_for(...)` | Two quarters, 10 sh: Q2 buys 0.1983, residual 0 |
| B5 | `processor.py::_reinvest` | Fee cap computed on gross, not net | compute withholding first, cap on net | Non-resident DRIP 10 sh: net 6.97 → fee 0.35 (buggy: 0.41) |

B2 and B5 share one root cause: **the steps run in the wrong order**. A great candidate notices that and fixes the order once, instead of patching two lines independently.

B4's hidden test only passes once B3 is also fixed: a rounded-up Q1 purchase leaves a negative residual that changes Q2. Good discussion: "this test fails for two reasons, so let me split it."

**Red herring:** `gross` uses `ROUND_DOWN` while withholding uses `ROUND_HALF_UP`. That looks inconsistent but it matches the spec.

## Follow-ups
- `positions_as_of` scans every move: O(M) per event. How would you index it? (Per-account sorted moves + bisect, or snapshots.)
- Why Decimal and not float here? What breaks with float?
- Where does the residual live if the service restarts? (In-memory dict: a persistence gap. Mention it, don't fix it.)
