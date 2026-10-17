# Bond Trade Booking

A fixed-income desk books bond trades. For each trade the system works out the **settlement date**, the **accrued interest** and the
**settlement amount** the buyer pays. Bond reference data (coupon, frequency, maturity, day count) is loaded from a security master.
The repository contains the booking service.

## Coupon schedule

- Coupon dates step **backward from maturity** every 12 / frequency months (frequency 1, 2 or 4).
- **End-of-month rule:** if the maturity date is the last day of its month, every coupon date is the last day of its month.
- If stepping back lands on a day that doesn't exist (e.g. 31 June), use the last day of that month.

## Settlement

Trade date + **1 business day**. Business days exclude Saturdays, Sundays and the **market holidays** loaded into the calendar.

## Day count conventions

- **30/360 (US):** with dates Y1-M1-D1 and Y2-M2-D2: if D1 is 31, set D1 = 30; if D2 is 31 **and** D1 (after adjustment) is 30, set D2 = 30.
  Days = 360 × (Y2 − Y1) + 30 × (M2 − M1) + (D2 − D1); year fraction = days / 360.
- **ACT/360:** actual calendar days / 360.

## Accrued interest

- Accrues from the **last coupon date on or before settlement** to the settlement date. Settling **on** a coupon date accrues nothing.
- Accrued = face × coupon rate × year fraction, rounded half-up to the cent.
- **Settlement amount** = clean price (% of face) × face / 100 + accrued, rounded half-up to the cent.

## Data model

| Entity | Fields |
|---|---|
| Bond | id, coupon rate, frequency, maturity, day count |
| Trade | trade id, bond, side, face, clean price, trade date, settlement date, accrued, settlement amount |

## Example

UST-like bond, 5% semi-annual, 30/360, matures 2030-05-15. $1,000,000 face at 99.50, traded Thu 2026-03-12 → settles Fri 2026-03-13.
Last coupon 2025-11-15 → 118 days → accrued **$16,388.89** → settlement amount 995,000.00 + 16,388.89 = **$1,011,388.89**.
