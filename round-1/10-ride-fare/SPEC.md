# Ride Fare

A ride-hailing app prices trips, applies promotions and pays drivers. `fares.py` handles the trip lifecycle and the receipt.

## Trip lifecycle

REQUESTED → ACCEPTED (driver assigned) → ARRIVED (driver at pickup) → STARTED → COMPLETED. A rider can cancel before the trip starts.

## Pricing (on completion)

1. **Fare** = ($2.50 + $1.20 per km + $0.30 per minute) × **surge multiplier**. Surge is **locked when the trip is requested**; later
   changes don't affect it.
2. **Minimum fare** $7.00, applied **after surge**.
3. **Waiting:** the first **2 minutes** between arrival and start are free; after that **$0.40 per started minute**. Not surged.
4. **Booking fee** $1.50, not surged, never discounted.
5. **Promo:** a percentage off fare + waiting, **at most $10.00** off.
6. **Total** = fare + waiting + booking fee − discount.

Every amount is rounded to the cent.

## Driver payout

The driver gets **75% of fare + waiting, before any promo** (the company pays for promos). The booking fee goes to the company.

## Cancellation

Free within 5 minutes of the driver accepting; after that **$5.00**.

## Example

No surge, 8 km, 15 minutes, no waiting: 2.50 + 9.60 + 4.50 = **$16.60** + $1.50 fee = **$18.10**. Driver gets **$12.45**.
