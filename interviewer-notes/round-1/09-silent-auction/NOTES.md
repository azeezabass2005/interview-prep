# 09 · Charity Silent Auction: interviewer notes

Code: `auction/`. Shape: second-price rule with a cap and a floor, tie-break by time, "latest wins" revision, lifecycle (closed lots).

**Watch this:** the visible `test_first_example` uses C = $170, while the spec's example has C = $175. With $170 the
hammer of $175 is consistent, so the test passes, but the spec's own example is untested. Even if they add it,
the spec example (B pays $180, invoice $198) passes on the buggy code, because the winner's bid equals the hammer there.
Good candidates notice that the examples don't exercise the cap, floor, tie or revision rules, and write targeted tests for each.

## PM answers

| Topic | Answer |
|---|---|
| Bids below reserve: do they count as runner-up? | Yes, they set the runner-up price, but the floor still applies. |
| Revision lower than the previous bid | Latest counts. The tie-break uses the latest bid's submission time. |
| Same bidder winning several lots | Fine, independent. |
| Closing twice | Out of scope (nice to guard). |
| Bid exactly equal to reserve | Sells (reserve is inclusive). |
| Premium rounding | Half-up to the cent. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `pricing.py::rank` | `reverse=True` on `(amount, seq)` puts the **later** of two tied bids first | `key=lambda b: (-b.amount_cents, b.seq)` | A 150 then B 150: A wins |
| B2 | `pricing.py::settle` | No cap at the winner's own bid | `min(hammer, winner.amount_cents)` | A 150, B 148: hammer 150 (buggy: 153) |
| B3 | `pricing.py::effective_bids` | Keeps the bidder's **highest** bid, not the latest | keep the bid with the greatest `seq` | A 200 → revises to 120, B 150: B wins |
| B4 | `pricing.py::settle` | No floor (reserve or opening) | `max(hammer, reserve or OPENING)` | Reserve 100, only A 150: hammer 100 (buggy: 5) |
| B5 | `pricing.py::settle` | Invoice uses the winner's max bid, not the hammer | `invoice_for(hammer)` | A 200, B 120: invoice 13,750 (buggy: 22,000) |
| G1 | `house.py::place_bid` | Bids accepted after close | raise if `lot.closed` | bid after close raises |

**Order of cap vs floor:** if the reserve is above the winner's bid the lot is unsold, so cap and floor never conflict. A candidate who asks "what if the floor exceeds the cap?" and reasons that through earns points.

## Follow-ups
- Why a list of bids and not a dict keyed by bidder? (Audit trail and tie-breaks need history. Derive the dict.)
- Ranking is O(n log n); for just the top two you need O(n). Is it worth it? (No, at gala scale.)
