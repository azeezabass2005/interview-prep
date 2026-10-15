# 02 · Brokerage Commission Statement: interviewer notes

Code: `fees/`. Shape: tiered (marginal) rates, clamp, ordered discount, and a separate fee with a different rounding rule.

## PM answers to clarifying questions

| Topic | Answer |
|---|---|
| Marginal vs flat tiers | Marginal, "like tax brackets". The $60k example ($32) proves it. |
| Band boundaries | $10,000 exactly is entirely in band 1. Bands are `(0, 10k]`, `(10k, 50k]`, `(50k, ∞)`. |
| Order: round → min/max → discount | Yes. The discount is 20% of the clamped commission, rounded half-up. |
| Does the discount apply to the reg fee? | No. |
| Which trades count toward 51? | All of the account's trades in the month, buys and sells, ordered by `executed_at`. |
| Ties in `executed_at` | Break by trade_id (not tested). |
| Partial fills | Each fill is a separate trade (assumption). |
| Month boundaries and timezone | The caller passes one month's trades, so out of scope. |

## Requirement map and planted issues

| ID | Location | What is wrong | Minimal fix | Test that fails for one reason |
|---|---|---|---|---|
| B1 | `commission.py::tiered_commission` | Flat: applies the band's rate to the *whole* notional | Accumulate each band's slice × rate | $60,000 → $32.00 (the buggy code gives $12.00) |
| G1 | `commission.py::commission_for` | `MAX_COMMISSION` is defined but never applied | `min(max(fee, MIN), MAX)` | $1,000,000 → $50.00 |
| B2 | `commission.py::regulatory_fee` | `ROUND_HALF_UP` where the spec says "always up" | `ROUND_UP` (ceiling for positive) | Sell $12,000 → 0.3336 → **$0.34** (the buggy code gives $0.33) |
| B3 | `statement.py::build_statement` | `i > 50` with 0-based `i`, so the discount starts at the 52nd trade | `i >= VOLUME_DISCOUNT_FROM_TRADE - 1` | 51 trades: the 51st has a discount |
| B4 | `statement.py::build_statement` | Uses input order, not execution order | `sorted(..., key=lambda t: t.executed_at)` | 52 trades given newest first: the *earliest-executed* trade must not be discounted |

The spec example ($5,000 sell → $0.14) is deliberately one where half-up and ceiling agree. The visible test passes, so the bug hides. Ask: "Why does that test not prove the rounding rule?"

**Red herrings:** `Decimal` everywhere is correct and deliberate (don't let the agent "simplify" to float). `frozen=True` on `Trade` is fine.

## Good signals
- Spots that the spec's own example ($60k → $32) is untested and turns it into the first test.
- Separates commission from the reg fee as two concepts with different rounding.
- Asks about the boundary at exactly $10,000 and $50,000.
- Explains why the reg-fee example in the visible tests is a weak test.

## Follow-ups
- Make the tier table data-driven: what invariants should the table satisfy (ascending, last unbounded)?
- Complexity: O(T) per trade for T tiers; O(n log n) statement because of the sort.
