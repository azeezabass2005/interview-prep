# Charity Silent Auction

A charity gala runs a sealed-bid auction. Bidders submit a private **maximum bid** per lot; the winner pays just enough
to beat the runner-up. The code in `auction/` implements the rules below.

## Rules

- **Bidding window:** a lot accepts bids until it's **closed**. Bids after closing are rejected.
- **Revisions:** a bidder may bid again on the same lot. **Only their latest bid counts**, even if it's lower.
- **Winner:** the highest bid. Ties go to the bid placed **first**.
- **Reserve:** a lot may have a reserve price. If the highest bid is below the reserve, the lot is **unsold**.
- **Hammer price** (what the winner pays the charity):
  - runner-up's bid **+ $5 increment**,
  - but **never more than the winner's own bid**,
  - and **never less than the reserve** (or the **$10 opening price** for lots with no reserve).
  - With only one bid, there's no runner-up: the floor (reserve or opening price) applies.
- **Invoice:** hammer price plus a **10% buyer's premium**, rounded half-up to the cent.

## Examples

| Reserve | Bids (in order) | Winner | Hammer | Invoice |
|---|---|---|---|---|
| $100 | A $150, B $180, C $175 | B | $180 (175 + 5, capped at B's 180) | $198.00 |
| $100 | A $200, B $120 | A | $125 | $137.50 |
| $100 | A $90 | none (unsold) | n/a | n/a |

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model lots, bids and results.
3. Outline the winner and price calculation and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
