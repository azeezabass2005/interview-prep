# Mini Matching Engine

An exchange matches incoming **limit orders** against a resting order book. The code in `engine/`
implements the rules below. Traders have reported odd fills.

## Rules

- An order has an id, trader, side (`BUY`/`SELL`), limit price (integer cents, > 0) and quantity (integer, > 0).
- **Crossing:** an incoming BUY trades with resting SELLs priced **≤** its limit; an incoming SELL trades with
  resting BUYs priced **≥** its limit.
- **Priority:** best price first (lowest ask / highest bid). At the same price, the **earliest** resting order
  trades first.
- **Execution price:** every fill happens at the **resting** order's price.
- **Partial fills:** an incoming order keeps matching until it's filled or no longer crosses. Whatever
  remains **rests on the book** at its limit price. A resting order that is partially filled **keeps its place in the queue**.
- **Self-trade prevention:** orders from the **same trader** must never trade with each other.
- **Cancel:** a resting order can be cancelled by id. Cancelling an unknown or fully filled order returns `False`.

## Example

Resting asks, in arrival order: `S1 SELL 100 @ 101`, `S2 SELL 50 @ 100`, `S3 SELL 70 @ 100`.

Incoming `B1 BUY 130 @ 101` produces fills: **S2 50 @ 100**, **S3 70 @ 100**, **S1 10 @ 101**. S1 keeps 90 on the book.

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model orders, the book, and fills, and why you chose those data structures.
3. Outline the matching loop and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
