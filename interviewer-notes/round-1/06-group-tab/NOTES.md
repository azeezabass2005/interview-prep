# 06 · Group Tab: interviewer notes

Code: `tab/`. Shape: pipeline order (coupon → tax → tip), threshold boundary, conservation of cents, deterministic remainder.

## PM answers

| Topic | Answer |
|---|---|
| Party size | Distinct people with at least one item. |
| Coupon larger than subtotal | Out of scope; assume coupon ≤ subtotal (raise if not, if they want). |
| Tip when auto-gratuity applies | 20% replaces the chosen tip, even if they chose more. |
| Proportional weights | Each person's **pre-coupon** subtotal. |
| Leftover cents in proportional split | Alphabetical, one cent each, same as even split. |
| Does the payer get a transfer? | No. Nobody sends money to themselves. |
| Zero-share people | Not possible: everyone has an item. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `allocation.py::allocate_proportionally` | Floors each share and drops the leftover, so shares sum < total | hand out the remainder alphabetically (like `split_evenly`) | example: `sum(shares) == total` (buggy: 7865 vs 7866) |
| B2 | `calculator.py::compute_breakdown` | Tip computed on `discounted + tax` | tip on `discounted` | example tip = 1116 (buggy: 1215) |
| B3 | `calculator.py::compute_breakdown` | `party_size > 6` | `>=` | 6 diners → tip_percent 20 |
| B4 | `calculator.py::compute_breakdown` | Tax computed before the coupon is applied | tax on `discounted` | coupon $10 on example: tax 462 (buggy: 550) |
| B5 | `calculator.py::settle_up` | Payer gets a transfer to themselves | skip `person == payer` | no transfer with sender == payer |

**The hint inside the code:** `split_evenly` handles remainders correctly and `allocate_proportionally` doesn't. A candidate who asks the agent "do these two helpers follow the same remainder rule?" finds B1 fast.

**Red herring:** `total_weight == 0` falls back to an even split. That's unreachable with valid items but harmless.

## Follow-ups
- What property test would you write? (For random bills, sum(shares) == total and every share ≥ 0.)
- Largest-remainder (Hamilton) vs alphabetical leftover: which is fairer? The spec says alphabetical; don't change it.
- Complexity: O(items × sharers + people log people).
