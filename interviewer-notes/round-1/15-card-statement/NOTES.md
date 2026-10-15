# 15 · Credit Card Statement: interviewer notes

Code: `card/statement.py`. Shape: average daily balance, a conditional exemption that applies to one bucket only, payment allocation order, min/max formulas, small-balance edge case.

## PM answers

| Topic | Answer |
|---|---|
| Cycle length | Varies (28–31); use `cycle.days` everywhere. |
| Daily balance timing | Apply that day's transactions, then record the end-of-day balance (as coded). |
| Payment allocation across APRs | Highest APR (cash, 29%) first. |
| Fee rounding | Half-up to the cent. |
| Overpayment | Becomes a credit on purchases (as coded). |
| Minimum when the balance is negative or zero | 0.00 (nice to handle). |
| Late fees / penalty APR | Out of scope. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `statement.py::PAYMENT_ORDER` | Pays the lowest APR first | order by APR desc (`["cash", "purchase"]`, or sort by `APR`) | 500/500 balances, pay 500: cash 0, purchase 500 |
| B2 | `statement.py::cash_advance_fee` | `min(5%, $10)` instead of `max` | `max` | $100 advance → cash balance 110.00 |
| B3 | `statement.py::build_statement` | Grace period zeroes cash interest too | apply grace to `purchase` only | paid in full, $1,000 cash → 23.84 |
| B4 | `statement.py::build_statement` | ADB divides by a fixed 30 days | divide by `cycle.days` | 31-day cycle, $1,000 → 20.38 (buggy: 21.07) |
| B5 | `statement.py::build_statement` | Floor of $25 even when the balance is lower | `min(minimum, new_balance)` | $20 balance, paid in full → 20.00 |

**Note:** the visible tests all use 30-day cycles. That's why B4 hides. A good candidate asks "what if the cycle isn't 30 days?" after reading "28–31" in the spec.

**Red herring:** `max(balance, 0)` in the daily sum is correct (credits earn nothing).

## Follow-ups
- Floating vs Decimal; where do you round? (Only final interest per bucket.)
- Complexity: O(days + txns). Event-based ADB would be O(txns log txns). Not worth it at 31 days.
