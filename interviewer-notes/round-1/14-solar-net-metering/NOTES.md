# 14 · Solar Net-Metering Bill: interviewer notes

Code: `utility/billing.py`. Shape: state carried across months (bank), order of operations (credit before tiers), tax base, a year-end stage, and lifecycle ordering.

## PM answers

| Topic | Answer |
|---|---|
| Is the bank in kWh or dollars? | kWh. Credit offsets kWh *before* tiers. |
| Year boundary | The true-up happens on the December bill; January starts with an empty bank. |
| Bank use order | It doesn't matter (one bucket). |
| Gaps in months (Mar, then May) | Allowed: the only rule is strictly after the last billed month. |
| True-up payout | Separate line; doesn't reduce `total`. |
| Tax rounding | Half-up to the cent on the rounded energy charge. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `billing.py::bill` | Tiers priced on **consumed**, not net usage | price `billable` | Jan example: 90.75 (buggy: 106.50) |
| B2 | `billing.py::bill` | Bank credit subtracted as dollars at the tier-1 rate, after tiering | subtract kWh from `billable` before tiering | Jun example: 98.63 |
| B3 | `billing.py::bill` | Tax base includes the fixed charge | `energy * TAX_RATE` | May bill = 12.00 (buggy: 12.60) |
| B4 | `billing.py::bill` | Used bank kWh never removed | `self.bank_kwh -= used` | May, Jun, Jul (300 kWh): Jul = 49.80 |
| G1 | `billing.py::bill` | December true-up missing | payout `bank × 0.04`, reset bank | Nov surplus 200 → Dec payout 8.00, bank 0 |
| G2 | `billing.py::bill` | Out-of-order months accepted (`last_billed` is set but never checked) | raise if `month <= last_billed` | bill May, then March → raises |

**Clue:** `last_billed` is written and never read (G2), and `TRUE_UP_RATE` / `TRUE_UP_MONTH` are imported nowhere (G1). "Which constants and fields are unused?" is a great agent prompt here.

**Red herring:** `tiered_energy_charge` is correct (it's tested). Watch for the agent claiming it's wrong because the code around it is.

## Follow-ups
- What should happen if a corrected reading arrives for a past month? (Re-bill: needs bill history and recomputing the bank. Out of scope, but a good design discussion.)
