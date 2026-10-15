# Bond Accrued Interest

A fixed-income desk tool computes how much a buyer pays for a bond: the quoted (clean) price plus the interest that has
**accrued** since the last coupon. The code in `bond/` implements the conventions below. Traders say some tickets are off by a few dollars.

## Conventions

- A bond has a face amount, an annual coupon rate, a coupon frequency (1, 2 or 4 per year) and a maturity date.
- **Coupon schedule:** coupon dates step **backward from maturity** every 12/frequency months.
  **End-of-month rule:** if the maturity date is the last day of its month, every coupon date is the last day of its month.
- **Settlement:** trade date **+ 1 business day** (Saturday and Sunday aren't business days; ignore holidays).
- **Day count, 30/360 (US):** with dates Y1-M1-D1 and Y2-M2-D2,
  - if D1 is 31, set D1 = 30
  - if D2 is 31 **and** D1 (after the adjustment above) is 30, set D2 = 30
  - days = 360 × (Y2 − Y1) + 30 × (M2 − M1) + (D2 − D1)
- **Accrued interest** = face × coupon rate × days(last coupon date → settlement) / 360, rounded **half-up** to the cent.
  The "last coupon date" is the latest coupon date **on or before** settlement. Settling **on** a coupon date accrues nothing.
- **Settlement amount** = clean price (% of face) × face / 100 + accrued interest.

## Example

$1,000,000 face, 5% semi-annual, matures 2030-05-15. Traded Thu 2026-03-12 → settles Fri 2026-03-13.
Last coupon 2025-11-15 → 30/360 days = 360 − 240 − 2 = 118 → accrued = 1,000,000 × 0.05 × 118 / 360 = **$16,388.89**.

## Candidate questions

1. Identify anything in the conventions that must be clarified before implementation.
2. Explain how you would model bonds, schedules and dates.
3. Outline the accrued interest calculation and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
