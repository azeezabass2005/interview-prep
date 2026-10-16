# Ride-Hailing Trip Billing

A ride-hailing app quotes riders a surge multiplier when they request a ride, follows the trip through its lifecycle, then bills the rider
and pays the driver. The repository contains the trip and billing service.

## Lifecycle

`REQUESTED` (with a quote) → `ASSIGNED` (a driver accepts, with an ETA) → `ARRIVED` (driver at pickup) → `IN_PROGRESS` (rider picked up)
→ `COMPLETED`. A rider can cancel before pickup.

## Quote

When the rider requests a ride, the app shows the **current surge multiplier** for the pickup zone. That multiplier is **locked** for the
trip, even if surge changes later. Surge is **capped at 3.0×**.

## Fare

1. **Metered:** $2.50 base + **$1.20 per mile** (to the hundredth of a mile) + **$0.30 per minute** of ride time (pickup to drop-off),
   where **any started minute counts as a full minute**.
2. **Surge:** the metered amount is multiplied by the locked surge.
3. **Wait time:** after the driver arrives, the rider has **2 free minutes**; each started minute **after** those 2 costs **$0.40**
   (never surged).
4. **Booking fee:** **$2.00**, never surged.
5. **Minimum:** surged metered + wait + booking fee is at least **$7.00**.
6. **Promo code:** a percentage off the amount from step 5, at most **$10.00** off. Tolls are never discounted.
7. **Tolls** are added at cost after everything else.

Each step's result is rounded half-up to the cent.

## Cancellation

A rider who cancels more than **2 minutes** after a driver was assigned pays **$5.00**, unless the driver hasn't arrived and is more than
**5 minutes** later than the ETA given at assignment. Cancelling before assignment is free.

## Driver payout

The driver receives **75%** of (fare − booking fee − tolls), plus **100% of tolls**, rounded half-up to the cent.

## Example

Locked surge 1.5×, rider ready immediately, 5.3 miles, 14 min 20 s, $3.00 toll, no promo:
metered 2.50 + 6.36 + 15 × 0.30 = 13.36 → × 1.5 = 20.04 → + 2.00 booking = 22.04 → + 3.00 toll = **$25.04**.
Driver: 75% × (25.04 − 2.00 − 3.00) = 15.03 + 3.00 = **$18.03**.
