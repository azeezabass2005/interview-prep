# Restaurant Tip Pool

At the end of each night a restaurant pools all tips and shares them among eligible staff. The code in `tips/` implements the rules below.
Staff have noticed their payouts don't match the house policy.

## Rules

1. **Pool:** card tips **minus 3%** (card processing cost) **plus** cash tips. Cash tips aren't charged the 3%.
2. **Eligibility:** managers are **never** eligible (it's illegal). Anyone who worked **fewer than 2 hours** that night isn't eligible.
3. **Weight:** each eligible employee's weight is **role points × hours** worked that night, summed over every role they worked.

| Role | Points |
|---|---|
| SERVER | 10 |
| BARTENDER | 8 |
| BUSSER | 5 |
| HOST | 3 |
| KITCHEN | 2 |
| MANAGER | not eligible |

   The 2-hour minimum applies to an employee's **total** hours across roles.
4. **Shares:** each employee gets pool × weight / total weight, **rounded down** to the cent. Leftover cents go one each to the
   employees with the **largest fractional remainders** (ties: alphabetical by name), so shares add up to the pool exactly.

## Example

Card tips $1,000.00, cash $200.00 → pool **$1,170.00**.
Alice SERVER 6 h (60) · Bob BARTENDER 5 h (40) · Cara BUSSER 4 h (20) · Dan MANAGER 8 h (excluded) · Eve HOST 1.5 h (excluded).
Total weight 120 → **Alice $585.00 · Bob $390.00 · Cara $195.00**.

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model shifts, weights and payouts.
3. Outline the distribution and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
