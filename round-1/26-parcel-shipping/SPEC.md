# Parcel Shipping Rates

An online store charges customers shipping at checkout using the carrier's rate card. The code in `ship/` implements the rules below.
The store keeps losing money on some shipments and overcharging on others.

## Rules

1. **Dimensional weight** = L × W × H ÷ 139, where each dimension (inches) is first **rounded up** to a whole inch.
2. **Billable weight** = the **greater** of actual weight and dimensional weight, **rounded up** to a whole pound.
3. **Base rate** by zone: first pound + each additional pound.

| Zone | First lb | Each additional lb |
|---|---|---|
| 1–2 | $5.00 | $0.50 |
| 3–4 | $7.00 | $0.80 |
| 5–6 | $9.00 | $1.10 |
| 7–8 | $12.00 | $1.60 |

4. **Oversize:** a package whose longest side is **more than 48 inches** adds **$15.00**.
5. **Fuel surcharge:** **12%** of (base rate + oversize fee), rounded half-up to the cent.
6. **Residential delivery:** **$4.50** per package, added after the fuel surcharge (no fuel surcharge on it).
7. An order's shipping is the sum over its packages.
8. **Free shipping:** if the order subtotal **after discounts** is **$75 or more** and the destination is **zone 1–4**, shipping is free.

## Example

12 × 10 × 8 in box, 6.2 lb, zone 5, residential: dim weight 960 / 139 = 6.91 → billable **7 lb**.
Base $9.00 + 6 × $1.10 = $15.60 · fuel 12% = $1.87 · residential $4.50 → **$21.97**.

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model packages, rates and the quote.
3. Outline the cost calculation and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
