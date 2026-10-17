# R1-12 · Bowling Score: Interviewer Guide

One file, `bowling.py` (~85 lines), with one passing test (all open frames). **The spec example (167) fails on the buggy code** (B1 via
the 8-2 spare followed by 0-6), so the example is a good first test.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Partial game `[10, 3]` | `[None, None]`: two frames started, neither known. |
| 10th-frame bonus rolls | Part of frame 10; never an 11th frame. |
| Average with no games | No handicap (0). |
| Handicap for a 205 average | 0. |
| Does this match count toward the handicap? | Only for later matches. |

## Code map
`_validate` · `_add` · `frame_scores` · `League.average` · `handicap` · `_final` · `match`.

## Planted bugs (5)

### B1 · Spare bonus takes two rolls
- **Where:** `frame_scores`: `rolls[i + 2:i + 4]`.
- **Test:** `5 5 | 3 4 | 0…` → [13, 20] (buggy [17, 24]).

### B2 · Bonus rolls become extra frames
- **Where:** `while i < len(rolls)` with no frame limit.
- **Test:** 12 strikes → 10 frames, **300** (buggy 12 frames, 330).

### B3 · Strike with missing bonus scored as known
- **Where:** strike branch passes `known=True`.
- **Test:** `[10, 3]` → `[None, None]` (buggy `[13, None]`).

### B4 · Negative handicap
- **Where:** `handicap`.
- **Test:** average 210 → **0** (buggy −9).

### B5 · Match counts itself in the handicap
- **Where:** `match` appends the new scores before computing handicaps.
- **Test:** ana's previous games [150]; she bowls 80 → handicap **45** (buggy 76).

Hints: (1) "what's the score of a perfect game?"; (2) "which games should the handicap see?"

## Red herrings
- `_validate` ignores the 10th frame's pin rule: deliberate (bonus rolls can exceed 10 in the last frame).
- `int()` for positive handicaps = rounding down: correct.

## Questions about the candidate's fixes (data structures)
- **Scoring:** "`frame_scores` is O(R). Could you make it incremental (live scoring after each roll)?" (Keep pending frames waiting for bonus in a small queue (deque); resolve when rolls arrive: O(1) per roll.)
- **Averages:** "`average` sums all games every call: O(G). Alternative?" (Keep running sum and count per bowler. Trade-off: corrections need adjustments.)
- **League standings over a season:** "Which structure for a sorted leaderboard updated weekly?" (Sort once per week: O(n log n), fine; or a heap for top-k.)
- **Immutability:** "`games` is a dict of lists, mutated from the outside in tests. Risks?" (Encapsulation; validation bypassed.)

## Feature requests
1. **"Team matches: 3 bowlers per team, team handicap = sum."** Strong answer: reuse `match` logic per team; points per game and for the series.
2. **"Handicap based on the last 9 games only."** Strong answer: a bounded window (deque with maxlen); what about fewer than 9 games.
3. **"Live scoring screen."** Strong answer: incremental scorer with the pending-bonus queue; None for unknown frames already supports it.

## Scoring signals
- **Strong:** starts with the example; tests a perfect game; asks what an unfinished game returns.
- **Weak:** only tests open frames.
