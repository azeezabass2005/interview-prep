# R1-05 · Order Matching: Interviewer Guide

One file, `orderbook.py` (~95 lines), with one passing test (a partial fill). **The spec example fails on the buggy code** (B1: trade
prices), so a candidate who turns it into a test finds the first bug fast. The rest need their own scenarios.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| IOC partially filled | The rest is cancelled; status CANCELLED (fills stay). |
| Self-trade | Cancel the resting order, keep matching. |
| Cancel a FILLED order | Error. |
| Market orders | Out of scope. |
| Depth ordering | Bids high → low, asks low → high. |

## Code map
`submit` (validate → match → rest or cancel) · `_crosses` · `_match` · `_rest` · `cancel` · `depth`.

## Planted bugs (5)

### B1 · Trades at the incoming price
- **Where:** `_match`: `"price": order.price`.
- **Test:** SELL @ 10.00 resting, BUY @ 10.50 → trade at **10.00**.

### B2 · LIFO at the same price
- **Where:** `_rest`: `appendleft`.
- **Test:** S1 then S2 at 10.00; a buy fills **S1** first.

### B3 · Partially filled IOC rests
- **Where:** `submit`: only cancels an IOC that filled nothing.
- **Test:** IOC 150 vs 100 available → CANCELLED, nothing left in the bids.

### B4 · Equal prices don't cross
- **Where:** `_crosses`: strict `<` / `>`.
- **Test:** SELL @ 10.00 and BUY @ 10.00 → one trade.

### B5 · No self-trade prevention
- **Where:** `_match`.
- **Test:** ann's SELL 10.00, cat's SELL 10.10, ann BUYS 10.20 → trades only with cat; ann's sell is CANCELLED.

Hints: (1) "which words in the spec say 'at or'?"; (2) "what's the order of a deque after `appendleft`?"

## Red herrings
- `depth` sorting direction: correct.
- `cancel` removes the price level when empty: correct.

## Questions about the candidate's fixes (data structures)
- **Price levels:** "`min(opposite)` on every loop iteration is O(levels). Alternatives?" (Heap of prices with lazy deletion, O(log n); sorted container/`bisect` insort into a sorted list: O(n) insert but O(1) best; a balanced tree in other languages.) "What does a heap make hard?" (Removing an arbitrary price on cancel → lazy deletion.)
- **Queues:** "Why a deque per level?" (O(1) append and popleft for FIFO.) "Cancel uses `queue.remove`: O(n). Fix?" (Doubly linked list + dict order_id → node; or lazy cancel flag skipped on pop.)
- **B2:** "Why is `appendleft` + `popleft` LIFO?" — make them explain it.
- **Orders dict:** "Memory grows forever. What would you do?" (Evict terminal orders after the session / archive.)

## Feature requests
1. **"Amend: change quantity or price of a resting order."** Strong answer: quantity down keeps priority; price change or quantity up loses priority (cancel + re-insert); tests.
2. **"Market orders."** Strong answer: no price limit; walk the book; never rest (IOC semantics); protection against an empty book.
3. **"Multiple symbols."** Strong answer: one book per symbol in a dict; order ids global; depth per symbol.

## Scoring signals
- **Strong:** converts the example first; designs a two-orders-same-price test; asks what happens to a partially filled IOC.
- **Weak:** fixes B1 and stops; can't explain deque ordering.
