# Hotel Rate Engine

A hotel's booking site quotes a total price for a stay and handles cancellations. The code in `hotel/` implements the rules below.
The front desk keeps overriding quotes by hand.

## Pricing

1. **Nightly base rate:** STANDARD $150, DELUXE $220, SUITE $400.
2. **Weekend nights** (the nights of **Friday and Saturday**) cost **20% more**.
3. **Length-of-stay discount** on the room subtotal: **3–6 nights: 5%**, **7 or more nights: 15%**.
4. **Promo code** `SAVE50`: **$50 off**, applied **after** the length-of-stay discount.
5. **Occupancy tax:** **14.75%** of the discounted room total.
6. **City fee:** **$3.50 per night**, **not taxed**.
7. Every money amount is rounded half-up to the cent when it's computed.

## Cancellation

Check-in time is **15:00** on the arrival date.
- Cancelled **168 hours (7 days) or more** before check-in: **full refund**.
- **48 – 168 hours** before: refund everything **except the first night** (its nightly rate including any weekend surcharge, plus tax on it).
- **Less than 48 hours** before: **no refund**.

## Example

DELUXE, arriving Thu 2026-06-04, 3 nights (Thu, Fri, Sat): 220 + 264 + 264 = 748.00 → 5% = −37.40 → 710.60 →
tax 104.81 → city fee 10.50 → **$825.91**.

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model stays, quotes and cancellations.
3. Outline the price calculation and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
