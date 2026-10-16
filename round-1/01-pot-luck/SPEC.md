# Pot Luck

A community fundraiser runs a pooled cash drawing several times a year. Participants register once, buy entries for the current draw,
and win a share of the pot depending on how closely their entry's code matches the winning code. The repository contains the service
that runs the drawings.

## Draw lifecycle

A draw is **OPEN** while entries are sold, **CLOSED** once the winning code is drawn, and **SETTLED** once payouts are calculated.
Only one draw can be open at a time, and a new draw can only open after the previous one is settled.

## Rules

- **Starting pot:** every draw starts with **$10,000** from a sponsor, plus **$5 for every active entry**, plus any **rollover** from the
  previous draw. The pot is fixed at the moment the draw is closed.
- **Entries:** an entry costs $5. A participant may hold at most **10 active entries in a draw**. Entries can be cancelled (and refunded)
  only while their draw is open; cancelled entries take no part in the draw.
- **Codes:** every entry is assigned a random 5-digit code from **00000** to **99999**. The winning code is drawn the same way when the draw closes.
- **Matching:** an entry's matches are the number of positions where its digit equals the winning code's digit in that position.
- **Payout tiers**, paid from the highest tier down:

| Matches | Share of pot |
|---|---|
| 5 | 100% |
| 4 | 40% |
| 3 | 20% |
| 2 | 5% |
| 0–1 | nothing |

- Each tier is entitled to its share of the pot, but never more than what is still left after the higher tiers have been paid.
  If 5-match winners take 100%, lower tiers get nothing.
- Winners in the same tier split the tier's amount equally, rounded down to the cent.
- Everything not paid out (unclaimed tiers and leftover cents) **rolls over** into the next draw.

## Data model

| Entity | Fields |
|---|---|
| Participant | participant id, name, e-mail (unique, case-insensitive) |
| Entry | entry id, draw id, participant id, code, status (active / cancelled) |
| Draw | draw id, number, status, winning code, pot, rollover carried in |
| Payout | entry id, participant id, matches, amount |
| Settlement | draw id, payouts, total awarded, rollover |

## Example

Draw 1 has 4 active entries and no rollover, so the pot is $10,000 + 4 × $5 = **$10,020**. The winning code is `12345`.

| Entry | Code | Matches | Payout |
|---|---|---|---|
| A | 12340 | 4 | $1,336.00 |
| B | 12395 | 4 | $1,336.00 |
| C | 92345 | 4 | $1,336.00 |
| D | 12000 | 2 | $501.00 |

The 4-match tier gets 40% = $4,008 split three ways. The 2-match tier gets 5% = $501. **$5,511 rolls over** into draw 2.
