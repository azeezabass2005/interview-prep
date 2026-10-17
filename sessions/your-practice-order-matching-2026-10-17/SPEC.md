# Mini Exchange Matching Engine

A small exchange runs a continuous limit order book per symbol. Members submit, amend and cancel orders; the engine matches them and
publishes trades. The repository contains the matching engine, the book, the trade tape and an API facade.

## Orders

An order has an id, member, symbol, side (BUY / SELL), limit price (integer cents, > 0), quantity (integer, > 0) and a type:
- **LIMIT:** whatever doesn't trade immediately **rests** on the book at its limit price.
- **IOC (immediate-or-cancel):** trades what it can immediately; any remainder is **cancelled**, never rests.

## Matching

- An incoming BUY trades with resting SELLs priced **at or below** its limit; an incoming SELL with resting BUYs **at or above**.
- **Priority:** best price first (lowest ask / highest bid); at the same price, the order that **arrived earliest**.
- Every trade happens at the **resting order's price**.
- The incoming order keeps trading until it's filled or nothing crosses. A partially filled resting order **keeps its place**.

## Amend and cancel

- **Cancel** removes a resting order. Cancelling an unknown or already-finished order is rejected.
- **Amend** changes a resting order's price and/or quantity:
  - reducing the quantity (same price) **keeps** time priority;
  - changing the price, or increasing the quantity, **loses** priority (the order moves to the back of its new level);
  - amending to a quantity at or below what has already been filled is rejected.
- An amended price that now crosses the book does **not** trade (keep it simple: amends never match).

## Trade tape

Every trade is published: symbol, buyer order, seller order, price, quantity. The tape also reports each symbol's last price and
volume-weighted average price (VWAP).

## Example

Resting asks in arrival order: `S1 100 @ 101`, `S2 50 @ 100`, `S3 70 @ 100`.
An incoming `LIMIT BUY 130 @ 101` trades **S2 50 @ 100**, **S3 70 @ 100**, **S1 10 @ 101**. S1 keeps 90 resting.
