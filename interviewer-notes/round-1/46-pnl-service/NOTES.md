# R1-46 · P&L Service: Interviewer Guide

The Round 1 version of Round 2 #16. One file, `pnl.py` (~85 lines), with one passing test. **The spec example fails
on the buggy code** (LIFO, the commission, and the closed lot all affect $295).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Commission on a partial sell | The whole commission reduces that sell's proceeds. |
| Fractional shares after a 3-for-2 split | Allowed (Decimal). |
| Reverse split (1-for-10) | Ratio 0.1, same rule. |
| Realized P&L rounding | Per sell, to the cent. |
| Oversell | Error and nothing changes. |

## Code map
`held` · `buy` (cost incl. commission) · `sell` (FIFO close, realized) · `split` · `unrealized`.

## Planted bugs (5)

### B1 · LIFO instead of FIFO
- **Where:** `sell`: `lots[-1]`.
- **Test:** 10 @ 100, 10 @ 120, sell 10 @ 130 → **300.00** (buggy 100.00).

### B2 · Sell commission ignored
- **Where:** `sell`: proceeds don't subtract `commission` (parameter unused: clue).
- **Test:** sell with $5 commission → **95.00**.

### B3 · Split doesn't adjust cost per share
- **Where:** `split`.
- **Test:** 10 @ 100, 2-for-1, price 55 → unrealized **100.00** (buggy 20 × (55 − 100) = −900).

### B4 · Partial close charges the whole lot
- **Where:** `sell`: `lot.quantity * cost` instead of `take * cost` (and after quantity is reduced it'd be wrong anyway: ordering subtlety).
- **Test:** sell 4 of 10 @ 110 → **40.00**.

### B5 · Short selling allowed
- **Where:** `sell` stops when lots run out and books P&L on shares never held.
- **Test:** hold 10, sell 15 → error.

Hints: (1) "the example is your first test — then split it"; (2) "which variable is the amount actually taken from the lot?"

## Red herrings
- Buy commission added to cost per share: correct.
- Lots removed when empty: correct.

## Questions about the candidate's fixes (data structures)
- **Lots as a list with `remove`/`lots[0]`:** "Complexity and a better choice?" (`deque` popleft O(1) for FIFO; `remove` is O(n).)
- **Other methods:** "Tax rules allow specific-lot or highest-cost-first. How would you support them?" (Strategy for lot selection: FIFO deque, LIFO stack, highest-cost heap.)
- **B5:** "Validate before mutating. Why does order matter here?" (Partial mutation on error.)
- **Splits on historical P&L:** "Should past realized P&L change after a split?" (No — only open lots.)

## Feature requests
1. **"Dividends: cash dividends count as realized income."** Strong answer: separate income line; per-symbol totals; no lot change.
2. **"Short positions."** Strong answer: negative lots; closing buys realize P&L; borrow costs.
3. **"Multi-currency: lots in USD, report in EUR."** Strong answer: FX at trade date for cost, current FX for market value; FX P&L component.

## Scoring signals
- **Strong:** isolates each cause of the example; tests a partial close and an oversell.
- **Weak:** single-lot tests only.
