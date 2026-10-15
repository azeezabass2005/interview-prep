# Solar Net-Metering Bill

An electric utility bills homes with rooftop solar. Each month the meter reports kWh **consumed** from the grid and kWh **exported** to it.
The code in `utility/` produces monthly bills. Customers with solar are disputing them.

## Rules

1. **Net usage** = consumed − exported.
2. **Banking:** if net usage is negative, the surplus kWh are **banked**. Banked kWh offset future net usage
   **before** tiered pricing is applied. Banked kWh used are removed from the bank.
3. **Energy charge** on billable kWh (net usage after banked credit), tiered like tax brackets:

| kWh in month | Rate |
|---|---|
| first 500 | $0.12 |
| 501 – 1,000 | $0.15 |
| above 1,000 | $0.20 |

4. **Tax:** 5% of the **energy charge only**.
5. **Fixed charge:** **$12.00** every month, even with zero or negative usage. Not taxed.
6. **Annual true-up:** on the **December** bill, any kWh still banked are **paid out at $0.04/kWh** (a separate payout line,
   not deducted from the bill), and the bank resets to zero.
7. Bills must be produced **in month order**. Billing a month that isn't after the last billed month is an error.
8. Money is rounded half-up to the cent.

## Example

| Month | Consumed | Exported | Bill |
|---|---|---|---|
| Jan | 700 | 100 | net 600 → 60.00 + 15.00 = 75.00 energy, 3.75 tax, 12.00 fixed → **$90.75** |
| May | 300 | 450 | net −150 → bank 150 → **$12.00** |
| Jun | 900 | 100 | net 800 − 150 banked = 650 → 60.00 + 22.50 = 82.50, tax 4.13, fixed 12.00 → **$98.63** |

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model readings, the bank, and bills.
3. Outline the bill calculation and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
