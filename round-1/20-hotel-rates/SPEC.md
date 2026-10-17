# Hotel Rates

A hotel's reservation system checks availability, prices stays and handles cancellations. `hotel.py` holds the logic.

## Stays and availability

- A stay from check-in date to check-out date covers the **nights** check-in … check-out − 1 (check-out day itself isn't a night).
- Each room type has an inventory (e.g. KING 5). A reservation is possible only if **every night** of the stay has a room of that type free.

## Rate plans

- **BAR** (best available rate): **$150** per night, **$190 on Friday and Saturday nights**.
- **ADVANCE:** 15% off BAR, only if booked **at least 14 days** before the check-in date; **non-refundable**.

## Price

Room total = sum of nightly rates (after the plan discount). Stays of **7 nights or more** get **10% off** the room total. Then
**12% tax**. Every step is rounded to the cent.

## Cancellation

- Check-in time is **15:00** on the check-in date.
- BAR: free until **48 hours before check-in time**; after that, the fee is the **first night's rate plus tax**.
- ADVANCE: no refund (the fee is the full price).

## Example

BAR, Monday 8 June → Monday 15 June 2026 (7 nights): 5 × 150 + 2 × 190 = 1,130.00 → 7-night discount → 1,017.00 → tax → **$1,139.04**.
