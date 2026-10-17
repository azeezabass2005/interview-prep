# Pot Luck

A community fundraiser runs a pooled cash drawing. Participants register, buy entries for the open draw, and win a share of the pot
depending on how closely their entry's code matches the winning code. `potluck.py` runs the drawings.

## Draws

A draw is **OPEN** while entries are sold, **CLOSED** once the winning code is drawn, and **SETTLED** once payouts are calculated.
Only one draw runs at a time; a new draw opens only after the previous one is settled.

## Rules

- **Participants** register with an e-mail address; e-mail addresses are unique, ignoring case.
- **Entries** cost **$5**. A participant may hold at most **10 active entries** in a draw. An entry can be cancelled (refunded) while its
  draw is open; cancelled entries take no part in the draw.
- **Codes:** every entry gets a random 5-digit code from **00000** to **99999**. The winning code is drawn the same way at close.
- **Pot** = $10,000 sponsor money + $5 per active entry + rollover from the previous draw, fixed when the draw closes.
- **Matches** = the number of positions where the entry's digit equals the winning code's digit in the same position.
- **Tiers**, paid from the highest down: 5 matches → 100% of the pot, 4 → 40%, 3 → 20%, 2 → 5%, fewer → nothing.
  A tier never gets more than what is still left after the higher tiers have been paid.
- Winners in a tier split its amount equally, **rounded down to the cent**.
- Everything not paid out rolls over into the next draw.

## Example

4 active entries, no rollover → pot **$10,020**. Winning code `12345`.

| Entry | Code | Matches | Payout |
|---|---|---|---|
| A | 12340 | 4 | $1,336.00 |
| B | 12395 | 4 | $1,336.00 |
| C | 92345 | 4 | $1,336.00 |
| D | 12000 | 2 | $501.00 |

**$5,511.00** rolls over.
