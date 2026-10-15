# Frequent Flyer Miles Ledger

An airline's loyalty program tracks miles earned on flights and spent on award tickets. The code in `miles/` implements the rules below.
Members complain about balances that look wrong.

## Rules

- **Earning:** **5 miles per whole dollar** of base fare (cents don't earn).
- **Status bonus:** on top of those base miles, Silver members earn **+25%**, Gold **+50%**, Platinum **+100%**
  (bonus rounded down). Base members earn no bonus.
- **Lots:** each earning is kept as a separate lot with its earn date.
- **Expiry:** miles expire on the **2-year anniversary** of the day they were earned. From that day on they can't be used.
  **Platinum members' miles never expire.**
- **Redemption:** spends the **oldest usable miles first**. If the member doesn't have enough usable miles,
  the redemption is **rejected and nothing is spent**.

## Example

A Gold member flies on a $412.80 fare on 2025-01-10: base 412 × 5 = 2,060 miles, bonus 1,030 → **3,090 miles**, usable through 2027-01-09.

A Base member earns 1,000 miles on 2024-01-10 and 1,000 on 2025-01-10, then redeems 1,000 on 2025-02-01. The 2024 miles are spent,
so on 2026-02-01 the member still has **1,000** usable miles.

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model members, lots and redemptions.
3. Outline the balance and redemption logic and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
