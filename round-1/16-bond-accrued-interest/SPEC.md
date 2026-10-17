# Bond Accrued Interest

A bond desk books trades in fixed-coupon bonds. The buyer pays the seller the price plus the interest **accrued** since the last coupon.
`bonds.py` works out settlement dates, coupon dates and accrued interest.

## Settlement

Trades settle **T+2 business days**: skip Saturdays, Sundays and the desk's holidays.

## Coupon schedule

A bond pays `rate ÷ frequency` of its face value `frequency` times a year (1, 2 or 4). Coupon dates are found by stepping **back from
maturity** in steps of 12 ÷ frequency months, each date computed **from the maturity date** (so a bond maturing on 31 August pays on
28/29 February and 31 August). If the day doesn't exist in a month, use the month's last day.

The **previous coupon date** for a settlement date is the latest coupon date **on or before** it. Settling on a coupon date means
nothing has accrued.

## Accrued interest

Accrued = face × rate × days ÷ 360, where days depends on the bond's day-count convention:
- **ACT/360:** actual calendar days from the previous coupon date to settlement.
- **30/360:** `360 × (Y2 − Y1) + 30 × (M2 − M1) + (D2 − D1)`, where D1 = 31 becomes 30, and D2 = 31 becomes 30 if D1 is 30 or 31.

A trade of N bonds at a clean price P (% of face): principal = N × face × P ÷ 100, accrued = N × accrued per bond. Amounts rounded to the cent.

## Example

$1,000 face, 5%, semiannual, 30/360, maturity 15 May 2031. Trade Mon 1 Jun 2026 → settles Wed 3 Jun; previous coupon 15 May →
18 days → $2.50 per bond. 10 bonds at 101.25 → principal $10,125.00 + accrued $25.00 = **$10,150.00**.
