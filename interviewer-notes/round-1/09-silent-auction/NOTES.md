# R1-09 · Charity Auction Platform: Interviewer Guide

~300 lines in `auction/`. One passing test (single bidder pays the opening price). **The spec's worked example passes on the buggy
code.** The increment and tie bugs only show at band edges and with equal maximums.

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Two bidders with the same maximum | Earlier bid wins; price = that maximum (runner-up + increment, capped). |
| A bidder raising their own max when already winning | Allowed; it doesn't change the price unless the runner-up changes. |
| Soft close chain | Each late bid sets closing = bid time + 2 min (can repeat). |
| Exactly 2 minutes before close | Counts as "last 2 minutes" (extends). |
| Reserve not met | Unsold; no invoice line. |
| Premium rounding | Half-up to the cent on the hammer. |
| FMV higher than hammer | Deductible 0 (never negative). |

## Code map
| Module | Responsibility |
|---|---|
| `services/bidding.py` | Register bidders, add lots, place bids (validation, soft close) |
| `services/pricing.py` | Per-bidder best bid, ranking, increment, current price |
| `services/closing.py` | Close a lot, reserve check |
| `services/invoices.py` | Per-bidder invoices, premium, deductible |
| `store.py`, `api.py`, `app.py` | Storage, facade, wiring |

## Planted bugs (5)

### B1 · Equal maximums go to the later bid
- **Where:** `pricing.py::leading_bids`: sorts by `(maximum, seq)` with `reverse=True`, so a higher seq (later) wins ties.
- **Test:** A max $150 (first), B max $150 → leader A, price $150.
- **Fix:** `key=lambda b: (-b.maximum, b.seq)` without reverse.
- **Hints:** "What does the spec say about equal maximums?"

### B2 · Increment chosen from the winner's max
- **Where:** `pricing.py::standing`: `increment_for(winner.maximum)`.
- **Test:** A $600, B $450 → runner-up band $10 → **$460** (buggy $475). Also A $120, B $99 → $104.
- **Fix:** `increment_for(runner_up)`.
- **Hints:** "Pick bids where the winner and runner-up are in different increment bands."

### B3 · Soft close extends from the old closing time
- **Where:** `bidding.py::bid`: `lot.closes_at + 2 min` instead of `now + 2 min`.
- **Test:** closes 20:00; bid at 19:59:30 → closes 20:01:30; a bid at 20:01:45 is rejected (buggy: accepted, close moved to 20:04).
- **Fix:** `lot.closes_at = now + timedelta(seconds=SOFT_CLOSE_SECONDS)`.
- **Hints:** "What closing time does the API return after a late bid?"

### B4 · Premium charged on the bidder's maximum
- **Where:** `invoices.py::build_invoices`: premium on `winning_bid.maximum`.
- **Test:** A $200, B $120, opening $50 → hammer $130 → premium **$13.00**, total $143.00 (buggy premium $20.00).
- **Fix:** premium on `lot.hammer`.
- **Hints:** "Make the winner's maximum much higher than the hammer."

### B5 · Negative deductible
- **Where:** `invoices.py`: `lot.hammer - lot.fmv` with no floor.
- **Test:** hammer $50, FMV $100 → deductible 0.00.
- **Fix:** `max(hammer - fmv, Decimal("0"))`.
- **Hints:** "A bargain lot: what's the donation?"

## Red herrings
- Rejecting bids ≤ the bidder's current maximum: correct.
- A single bidder pays the opening price: correct.
- `leading_bids` keeping each bidder's highest bid: correct, since lowering is impossible.

## Questions about the candidate's fixes (data structures)
- **B1/B2:** "`standing` re-ranks every bid on every call: O(b log b). You only need the top two per lot. How?" (Maintain the top-2 per lot incrementally on each bid: O(1) per bid. Watch out: the same bidder raising their max must update their entry, not add one.) "What structure if you needed the top k?" (A heap of size k, or a sorted list with bisect.)
- **B3:** "How would the platform close thousands of lots on time?" (A priority queue (heap) of `(closes_at, lot_id)`; soft close changes a key: push a new entry and ignore stale ones when popped (lazy deletion), since decrease-key isn't supported by `heapq`.)
- **Invoices:** "`build_invoices` scans all lots: O(L). Fine for one gala. If invoices were needed per bidder on demand?" (Index lots by winner on close.)
- **General:** "Bids are a list per lot. Why keep all bids rather than just the max?" (Audit and tie-breaking history; disputes.)

## Feature requests
1. **"Buy-it-now: a lot can be bought immediately at a fixed price until the first bid arrives."** Strong answer: a state machine (BUY_NOW_AVAILABLE → BIDDING → CLOSED); a race between a bid and a buy-now (atomic transition); invoice integration.
2. **"Live-paddle raise: donors pledge fixed amounts ($100/$250/$1000) during the gala, without a lot."** Strong answer: a separate pledge entity; fully deductible (FMV 0); invoices merge pledges and lots.
3. **"Outbid notifications by SMS."** Strong answer: emit an event when the leader changes (compare before/after in `bid`); deduplicate; never notify on own raises; async delivery.

## Scoring signals
- **Strong:** realises the spec example passes and designs band-edge and tie tests; checks the returned closing time after late bids.
- **Weak:** trusts the example; never looks at invoices.
