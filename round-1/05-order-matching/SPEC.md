# Order Matching

A small exchange runs a continuous **limit order book** for one stock. Traders submit buy and sell orders; the engine matches them
into trades. `orderbook.py` is the matching engine.

## Orders

An order has an id, trader, side (BUY/SELL), limit price (a multiple of $0.01), quantity (> 0) and time in force:
- **GTC** (good till cancelled): whatever doesn't trade immediately **rests** in the book.
- **IOC** (immediate or cancel): whatever doesn't trade immediately is **cancelled**.

Statuses: NEW (resting, nothing filled) · PARTIAL · FILLED · CANCELLED.

## Matching

- An incoming BUY trades with resting SELLs priced **at or below** its limit; an incoming SELL with BUYs **at or above** its limit.
- **Price-time priority:** best price first (lowest ask / highest bid); at the same price, the **earliest** order first.
- Trades happen at the **resting order's price**.
- **Self-trade prevention:** an incoming order never trades with a resting order from the **same trader**. That resting order is
  **cancelled** and matching continues.

## Other operations

- Cancel a resting order (NEW or PARTIAL).
- **Depth:** for one side, the best N price levels with the total remaining quantity at each.

## Example

Resting: SELL 100 @ 10.02 (S1), SELL 200 @ 10.01 (S2). BUY 250 @ 10.02 (GTC) → trades **200 @ 10.01** with S2, then **50 @ 10.02**
with S1. The buy is FILLED; S1 rests with 50.
