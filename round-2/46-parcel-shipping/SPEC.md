# Checkout Shipping

An online store prices shipping at checkout by rating every package with two carriers and picking the cheaper one, and shows an estimated
delivery date. The repository contains the rating and estimation service.

## Billable weight (per carrier)

- **Dimensional weight** = L × W × H ÷ the carrier's divisor, where each dimension (inches) is first **rounded up** to a whole inch.
  Divisors: SPEEDY **139**, VALUE **166**.
- **Billable weight** = greater of actual and dimensional weight, **rounded up** to a whole pound (at least 1).

## Package rate (per carrier)

1. **Base:** first pound + each additional pound, by zone (see `config.py` for both carriers' tables).
2. **Oversize:** longest side **more than 48 in** adds **$15.00**.
3. **Fuel surcharge:** SPEEDY 12%, VALUE 9%, of (base + oversize), rounded half-up to the cent.
4. **Residential:** **$4.50** per package, added after fuel (no fuel on it).

## Order shipping

- Each package is rated with both carriers; the order uses **one** carrier for all packages: the one with the lower order total
  (ties: SPEEDY).
- **Free shipping:** if the order subtotal **after discounts** is **$75 or more** and the zone is **1–4**, shipping is free.

## Delivery estimate

- Orders placed **at or after 14:00** (warehouse time), or on a weekend, ship on the **next business day**; otherwise the same day.
- Transit: SPEEDY 2 business days, VALUE 4. Business days are Monday–Friday.

## Example

12 × 10 × 8 in, 6.2 lb, zone 5, residential, SPEEDY: dim 960/139 = 6.91 → **7 lb**. Base 9.00 + 6 × 1.10 = 15.60; fuel 1.87;
residential 4.50 → **$21.97**.
