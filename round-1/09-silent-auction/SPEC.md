# Silent Auction

A charity runs an online auction with **proxy bidding**: each bidder enters the most they're willing to pay (their *max*), and the
system bids on their behalf only as much as needed. `auction.py` runs the auction.

## Items

An item has a starting price, a closing time and an optional **reserve** (the lowest price the charity will accept).

## Bidding

- **Increments** depend on the current price: below $100 → $5; $100 up to $499.99 → $10; $500 and above → $25.
- The first bid must be at least the starting price. Later bids must be at least the current price + the increment. A leader may raise
  their own max at any time; that doesn't change the price.
- **Current price:** with one bidder, the starting price. Otherwise the second-highest max + the increment for that amount, **but never
  more than the highest max**.
- Equal maxes: the bidder who bid **first** leads.
- **Soft close:** a bid placed in the last 5 minutes moves the closing time to **5 minutes after that bid**. No bids at or after closing.

## Closing

The leader wins at the current price if it meets the reserve; otherwise the item is **not sold**. The winner's invoice adds a **10% buyer's
premium** (rounded to the cent).

## Example

Start $50. Ana max $120, then Ben max $150 → price = 120 + 10 = **$130**, Ben leads. Invoice: 130 + 13 = **$143.00**.
