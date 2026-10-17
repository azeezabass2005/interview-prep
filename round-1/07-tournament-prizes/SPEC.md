# Tournament Prizes

A card room runs poker tournaments. Players register, may **re-enter** after busting during late registration, and are eliminated one
by one until a winner remains. `tournament.py` tracks entries, finishing positions and prize money.

## Entries

- Buy-in $100: **$85 goes to the prize pool**, $15 to the house. Every entry counts, **including re-entries**.
- **Late registration** is open until the tournament director closes it. While it's open, a busted player may re-enter, at most
  **2 re-entries** per player (3 entries in total). After it closes, nobody can register or re-enter.
- Some tournaments have a **guarantee**: the pool is never less than the guaranteed amount (the house adds the difference).

## Eliminations and finishing positions

- Eliminations while late registration is open don't get a finishing position (the player may re-enter).
- After it closes, a player knocked out finishes in position = number of players still in before the hand.
- If several players are knocked out in **the same hand**, the one who **started the hand with more chips finishes higher**.
- The last player standing finishes 1st.

## Prizes

| Entries | Paid places (% of pool) |
|---|---|
| 2–9 | 65, 35 |
| 10–29 | 50, 30, 20 |
| 30 or more | 40, 25, 15, 10, 10 |

Each prize is rounded **down to the dollar**; the dollars left over go to **1st place**.

## Example

8 players, guarantee $1,000. Pool = 8 × 85 = $680 → guarantee → **$1,000**. Prizes: 1st **$650**, 2nd **$350**.
