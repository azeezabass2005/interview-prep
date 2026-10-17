# IPO Allocation

A bank runs the order book for a company's IPO. Investors place orders while the book is open; when the price is set, shares are
allocated. `ipo.py` holds the order book and the allocation.

## Orders

An order has an id, investor, type (**RETAIL** or **INSTITUTIONAL**), number of shares and an optional **limit price** (the most the
investor will pay). Orders can be amended (new size and/or limit) or cancelled until allocation.

**Priority:** every order has a time priority. Amending an order **up** (more shares) gives it a new, later priority; amending down or
changing only the limit keeps it.

## Allocation at the final price

1. Orders whose limit is **below** the final price are excluded (a limit equal to the price is fine). Cancelled orders are excluded.
2. **Tranches:** 20% of the offering for retail, 80% for institutional. If one tranche's demand is smaller than its shares, the spare
   shares go to the other tranche.
3. Within a tranche, if demand fits, everyone gets what they asked for. Otherwise allocation is **pro rata** (shares × available ÷ demand), rounded down:
   - retail to **lots of 100 shares**,
   - institutional to **whole shares**.
4. Leftover shares are handed out one lot (retail) or one share (institutional) at a time, to orders **largest first, then by priority**,
   repeating until none are left. Nobody gets more than they asked for.

## Example

10,000 shares at $20. Retail: R1 3,000, R2 1,000 (2,000 available → R1 **1,500**, R2 **500**). Institutional: 8,000 asked → everyone filled.
