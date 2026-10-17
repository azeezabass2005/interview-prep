# Parcel Shipping

An online shop shows shipping options at checkout and picks the best one. `shipping.py` prices parcels with two carriers and
estimates delivery dates.

## Billable weight

`max(actual kg, dimensional kg)`, where dimensional kg = length × width × height (cm) ÷ 5000. Rounded **up** to the next 0.5 kg.

## Price per carrier

| Carrier | Base | Per kg zone 1 | Per kg zone 2 | Oversize | Business days zone 1 / 2 |
|---|---|---|---|---|---|
| SWIFT | $8.00 | $2.00 | $3.00 | $15.00 | 1 / 2 |
| BUDGET | $5.00 | $1.50 | $2.50 | $20.00 | 3 / 5 |

- **Fuel surcharge 10%** of base + weight charge only.
- **Oversize** (any side over 120 cm) and **residential** ($3.00, both carriers) surcharges are added after fuel; no fuel on them.
- Prices rounded to the cent.

## Delivery

- Orders placed **after 15:00** ship the next business day; otherwise the same day (if it's a business day).
- Delivery date = ship date + the carrier's business days (Monday–Friday only).

## Choosing

- Only options delivering on or before the customer's deadline (if any) are offered.
- Orders of **$100 or more** ship **free with BUDGET** — if BUDGET meets the deadline.
- Otherwise the cheapest option; ties go to SWIFT.

## Example

3 kg, 40 × 30 × 20 cm (dimensional 4.8 → billable 5.0 kg), zone 2, residential:
BUDGET 5.00 + 12.50 = 17.50, fuel 1.75, + 3.00 = **$22.25**; SWIFT 8.00 + 15.00 = 23.00, fuel 2.30, + 3.00 = **$28.30**.
