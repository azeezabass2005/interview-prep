# Pot Luck

A community fundraiser runs a pooled cash drawing to determine prizes.
The code in `potluck/` claims to implement the rules below. It doesn't fully do so.

## Problem context & rules

- **Starting pot:** each draw starts at **$10,000** from a sponsor, plus **$5 added per entry**.
- **Code assignment:** the system assigns each entry a random 5-digit code (**00000–99999**).
- **Drawing:** a winning 5-digit code is generated; the pot is calculated **at drawing time**.
- **Reverse-order rule:** tiers are handled in reverse (5 matches first). If 5-match winners
  claim 100%, lower tiers get nothing.
- **Splitting:** winners in the same tier split that tier's share.
- **Rollover:** any amount not awarded rolls over into the next draw's pot.

## Payout tiers (% of pot)

| Matches | Share of pot |
|---------|--------------|
| 5       | 100%         |
| 4       | 40%          |
| 3       | 20%          |
| 2       | 5%           |
| 1       | 0% (no payout) |

## Example scenario

3 entries match 4 numbers and 1 entry matches 2 numbers:

- the 4-match entries split 40% (13.33% each)
- the 2-match entry receives 5%

## Candidate questions

1. Identify anything in the problem context that must be clarified before implementation.
2. Explain how you would model entries, a draw, and payout results.
3. Outline the payout calculation and the tests you would want.
4. Identify bugs or issues and fix them.

## Running the tests

```
python -m unittest discover -s tests -v
```
