# IPO Bookbuilding and Allocation

An underwriter runs the order book for a share offering. Investors submit orders with a price limit while the book is open; at close the
underwriter sets the final price and allocates the shares. The repository contains the book and the allocation engine.

## Orders

- An order has an investor, a number of shares (a positive multiple of the **lot size, 100**) and a **limit price** (the most they will pay).
- One order per investor. Orders can be **amended** (shares and/or limit) or **cancelled** while the book is open. An amended order counts
  as a **new** order for time priority.
- An order of **1,000 shares or fewer** is **retail**; larger orders are **institutional**.

## Pricing

At close the underwriter sets the final price. Orders whose **limit is below the final price drop out** entirely.

## Allocation

- **20%** of the offering is reserved for retail (the **retail tranche**); the rest is the **institutional tranche**.
- If retail demand is below the retail tranche, the **unused retail shares move to the institutional tranche**.
- Within each tranche:
  - **Undersubscribed** (demand ≤ tranche): every order is filled.
  - **Oversubscribed** (retail): first each order gets **one lot** in time order while shares remain; then the rest is split
    **pro-rata to remaining demand, rounded down to whole lots**; then leftover lots go **one at a time to the largest unfilled demand**
    (ties: earliest order).
  - **Oversubscribed** (institutional): pro-rata to demand rounded down to whole lots, then leftover lots as above (no guaranteed lot).
- Nobody gets more than they asked for; shares not allocated stay with the issuer.

## Data model

| Entity | Fields |
|---|---|
| Offering | offering id, shares offered, status (OPEN / CLOSED), final price |
| Order | investor, shares, limit price, sequence, status (ACTIVE / CANCELLED) |
| Allocation | investor, shares allocated |

## Example

Offering 10,000 shares at a final price of $20. Retail tranche 2,000, institutional 8,000.
Retail orders: r1 1,000, r2 600 (demand 1,600 < 2,000, so both filled; 400 unused shares move to institutional → 8,400).
Institutional orders: i1 6,000 @ $21, i2 4,000 @ $22, i3 5,000 @ $19 (drops out).
Demand 10,000 for 8,400: pro-rata i1 5,040 → 5,000, i2 3,360 → 3,300; 100 left over → i1 (largest unfilled: 1,000 vs 700).
**Final: r1 1,000 · r2 600 · i1 5,100 · i2 3,300.**
