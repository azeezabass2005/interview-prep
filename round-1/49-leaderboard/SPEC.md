# Leaderboard

A bank runs a paper-trading competition for interns. Everyone starts with **$100,000** of virtual cash; the leaderboard ranks them by
return. `leaderboard.py` records trades and prices and produces standings.

## Portfolio

- Buys reduce cash by quantity × price; sells increase it. Positions can't go below zero.
- **Value** = cash + Σ quantity × **latest market price** of each symbol (from `set_price`; before any market price is set for a symbol, use
  the last traded price).
- **Return** = (value − 100,000) ÷ 100,000 × 100, rounded to 2 decimals.

## Standings

- Only participants with **at least 5 trades** who are **not disqualified** appear.
- Order: higher return first; ties → **fewer trades** first; then whoever joined earlier.
- Ranks are 1, 2, 3, … in that order. `page(n, size)` returns page **n (starting at 1)** of the standings.

## Other views

- `rank_of(name)`: the participant's rank, or `None` if they're not in the standings.
- `summary(name)`: cash, non-zero positions, value, return, trades, rank and disqualified flag.
- `movers(previous)`: given yesterday's ranks `{name: rank}`, how many places each ranked participant moved up (negative = down),
  biggest climbers first (ties alphabetical).

## Example

Ana buys 100 XYZ @ $10 (and makes 4 more small trades at unchanged prices). XYZ's market price moves to $12 → value $100,200 →
return **0.20%**.
