# Tournament Prize Pool

A card-room runs weekly tournaments. The code in `prizes/` computes each finisher's prize from the entries and the final standings.

## Rules

- **Entry fee:** **$55** per entry. Players may **re-enter** after busting; every entry pays the fee and counts as an entry.
- **Rake:** the house keeps **10% of the entry fees** (rounded down to the cent).
- **Guarantee:** the prize pool is at least **$2,000**. If entry fees minus rake fall short, the house adds the difference.
- **Places paid** depend on the number of entries:

| Entries | Paid places (% of prize pool) |
|---|---|
| up to 10 | 65 / 35 |
| 11 – 30 | 50 / 30 / 20 |
| 31 or more | 40 / 25 / 15 / 12 / 8 |

- **Ties:** players who tie share the places they occupy. Two players tied for 2nd split (2nd + 3rd) equally, and
  the next finisher is **4th**. A tie that straddles the last paid place shares only the paid places it covers.
- **Cents:** each place amount is rounded down to the cent. Leftover cents go to the **1st place** finisher.
  When a tie split leaves cents, they go one each to the tied players in alphabetical order.
- The prizes paid must add up to exactly the prize pool.

## Example

61 entries → fees $3,355.00, rake $335.50, prize pool **$3,019.50**. Five places: $1,207.80 (+1¢ leftover) / $754.87 / $452.92 / $362.34 / $241.56.

20 entries → fees $1,100, rake $110 → net $990, so the **guarantee** applies: pool **$2,000**. Finish: ana 1st; ben and cy tied 2nd; dee 4th.
ana $1,000; ben $500; cy $500; dee $0.

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model entries, standings and payouts.
3. Outline the payout calculation and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
