# R1-07 · Tournament Prizes: Interviewer Guide

One file, `tournament.py` (~80 lines), with one passing test (single eliminations). The spec example passes on the buggy code
(the guarantee hides the pool bug, and 8 entries is mid-bracket).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Is 1 entry a tournament? | Out of scope (no prizes). |
| Exactly 10 entries | 3 places. |
| Equal chips in the same hand | Won't happen in this version. |
| Prizes before the tournament ends | `prizes()` can be called any time; based on current entries. |
| Re-entry while still in | Not allowed. |

## Code map
`register` (re-entry rule) · `close_registration` · `eliminate` (positions) · `prize_pool` · `_percentages` · `prizes` · `results`.

## Planted bugs (5)

### B1 · Three re-entries allowed
- **Where:** `register`: `count > 1 + MAX_REENTRIES`.
- **Test:** enter, then bust and re-enter twice; the third re-entry is refused.

### B2 · Pool counts players, not entries
- **Where:** `prize_pool`: `len(self.players)`.
- **Test:** 10 players + 2 re-entries → **$1,020** (buggy $850).

### B3 · Bracket boundary
- **Where:** `_percentages`: `count > minimum`.
- **Test:** exactly 10 entries → 425 / 255 / 170 (buggy: the 2–9 table, two places).

### B4 · Leftover dollars to last place
- **Where:** `prizes`: `amounts[-1]`.
- **Test:** 11 entries ($935) → 468 / 280 / 187 (buggy 467 / 280 / 188).

### B5 · Same-hand eliminations ordered the wrong way
- **Where:** `eliminate`: `reverse=True` gives the worst place to the bigger stack.
- **Test:** 4 left, p0 (1,000 chips) and p1 (500) out together → p1 4th, p0 3rd.

Hints: (1) "count the entries in your test, not the players"; (2) "what's special about exactly 10?"

## Red herrings
- Eliminations during late registration don't get positions: correct.
- The guarantee as `max(pool, guarantee)`: correct.

## Questions about the candidate's fixes (data structures)
- **`entries.count(player)`** is O(E) per registration. "Better?" (`Counter` / dict player → entries: O(1).)
- **`players` property** builds a set every call. "When is that a problem?" (Hot paths; but here it's O(E) on demand — fine for hundreds of players.)
- **`active` as a set.** "Why a set?" (O(1) membership/remove; order doesn't matter.) "What if we needed seat assignments?" (Dict player → table/seat; balancing tables needs per-table counts — heap of tables by player count.)
- **B5:** "Sorting the hand's eliminated players is O(k log k). Fine?" (k is tiny.)

## Feature requests
1. **"Bounties: $20 of each buy-in is a bounty on the player; whoever knocks them out collects it."** Strong answer: the pool share changes; knockout attribution in `eliminate` (who won the hand); split bounty when two players knock out one.
2. **"Deal-making at the final table (chip-chop)."** Strong answer: prizes proportional to chips for remaining players, with a guaranteed minimum; overrides the table for those places.
3. **"Payout table defined per tournament."** Strong answer: validate percentages sum to 100; brackets sorted; reuse rounding.

## Scoring signals
- **Strong:** distinguishes entries from players; probes exactly 10; builds the same-hand case.
- **Weak:** reproduces the example and the visible test only.
