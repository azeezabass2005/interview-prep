# Hotel Reservations

A boutique hotel sells rooms through its own website. The service checks availability per night, prices stays under two rate plans,
books reservations and handles cancellations. The repository contains it.

## Inventory

Room types and counts: STANDARD (10 rooms, $150/night), DELUXE (5, $220), SUITE (2, $400). A stay of N nights needs one room of the
type available on **every** night of the stay. A reservation holds one room per night from check-in up to (not including) check-out.

## Pricing (per reservation)

1. **Nightly rate:** base rate; nights of **Friday and Saturday** cost **20% more**.
2. **Length-of-stay discount** on the room subtotal: 3–6 nights **5%**, 7+ nights **15%**.
3. **Rate plan:** FLEXIBLE (no change) or NON_REFUNDABLE (**10% off**, applied after the length-of-stay discount).
4. **Promo code** `SAVE50`: **$50 off**, applied **last** (after the rate-plan discount).
5. **Occupancy tax 14.75%** on the discounted room total. **City fee $3.50 per night**, not taxed.
Each amount is rounded half-up to the cent when computed.

## Cancellation

Check-in time is **15:00** hotel time on the arrival date.
- NON_REFUNDABLE: no refund.
- FLEXIBLE: **168 hours or more** before check-in → full refund; **48–168 hours** → refund everything except the first night
  (its nightly rate plus tax on it); **less than 48 hours** → no refund.
Cancelled reservations release their rooms.

## Data model

| Entity | Fields |
|---|---|
| Room type | code, rooms, base rate |
| Reservation | id, guest, room type, check-in, check-out, plan, promo, nightly rates, totals, status |

## Example

DELUXE, FLEXIBLE, arriving Thu 2026-06-04 for 3 nights (Thu, Fri, Sat): 220 + 264 + 264 = 748.00 → 5% → 710.60 → tax 104.81 →
city fee 10.50 → **$825.91**.
