# Event Ticketing

A theatre sells reserved seats online. Customers **hold** seats while they check out, then **buy** them. `boxoffice.py` manages seats,
holds, orders and refunds for one event.

## Seats and prices

Seats are named row letter + number (`A1` … `A10`). Prices by row: **A–C $120**, D–J $80, K onwards $50. Every ticket has a **$4.50
service fee**.

## Holds

- A hold reserves seats for **10 minutes**. After that it expires and the seats are free for anyone.
- A seat can't be held or bought by two customers at once.
- **No single gaps:** a hold is refused if it would leave a **single empty seat between two taken seats** in a row (taken = sold or held).
- At most **8 tickets per customer per event**, counting tickets already bought and seats currently held.

## Buying

A customer buys all the seats of their own unexpired hold. Total = ticket prices + fees.

## Refunds

Orders can be refunded until **48 hours before the show**. The ticket prices are refunded; **service fees are not**. Refunded seats are free again.

## Example

Ana holds D4 and D5 at 19:00 and buys at 19:06 → 2 × 80 + 2 × 4.50 = **$169.00**. Refunded three days before the show → **$160.00** back.
