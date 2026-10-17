# Brokerage Commission

A retail broker charges commission and passes on a regulatory fee for every trade. Trades can later be **busted** (cancelled by the
exchange). Each month every account gets a statement. `commission.py` calculates the charges.

## Equity commission

- **Per-share rate** depends on the account's equity volume **earlier in the same calendar month**:

| Monthly shares (cumulative) | Rate per share |
|---|---|
| first 300,000 | $0.005 |
| above 300,000 | $0.003 |

  An order that crosses the 300,000 boundary pays each share at the rate of the band it falls into.
- **Minimum** $1.00 per order, but the commission **never exceeds 1% of the trade value**, even if that's below the minimum.
- Commission is rounded to the nearest cent.

## Options commission

$0.65 per contract, minimum $1.00 per order. One contract = 100 shares (value = contracts × premium × 100). Options don't count toward
equity volume.

## Regulatory fee

On **SELL** trades only (equity and options): trade value × 0.0000278, **rounded up** to the next cent.

## Busted trades

A busted trade is refunded (commission and fee), leaves the statement and **doesn't count toward monthly volume**. Commissions already
charged on later trades are not recalculated.

## Example

BUY 1,000 shares @ $150.00 → $5.00. SELL 1,000 @ $151.00 → commission $5.00, fee 151,000 × 0.0000278 = 4.1978 → **$4.20**.
Statement total for the month: **$14.20**.
