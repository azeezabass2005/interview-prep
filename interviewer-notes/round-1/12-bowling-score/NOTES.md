# R1-12 · Bowling League Scoring: Interviewer Guide

~285 lines in `league/`. One passing test (all open frames). Two layers to test: the game engine (lookahead bonuses, 10th frame,
validation) and the league layer (handicaps as of a point in time, tie points).

## Session plan (60 min)
0–5 resume · 5–15 spec + questions · 15–20 code map · 20–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Strike bonus: next rolls or next frame? | Next **two rolls**, across frames (X, X, 5 → 25 for frame 1). |
| 10th-frame validation (X, 5, 6)? | Out of scope; only frames 1–9 are validated. |
| Average rounding | Floor. Handicap floor too. |
| Handicap for absentees | Out of scope (every bowler bowls). |
| Points for a tied game | ½ each; total per match is always 4. |
| Is the handicap updated during the week? | No: it's fixed for all 3 games, using games before this week. |

## Code map
| Module | Responsibility |
|---|---|
| `game.py` | Rolls, frames, completeness, frame totals |
| `render.py` | Scorecard symbols (correct) |
| `services/handicap.py` | Average and handicap (correct as functions) |
| `services/matches.py` | Bowlers, teams, recording a match, team points, standings |
| `store.py`, `api.py`, `app.py` | Storage, facade, wiring |

## Planted bugs (5)

### B1 · Strike bonus takes the next *frame's* rolls
- **Where:** `game.py::frame_totals`: `bonus_rolls = nxt[:2]`. After a strike followed by a strike, the next frame has one roll, so the frame is treated as pending (or short).
- **Test:** X, X, 5, 3, 14 × 0 → frame 1 = 25, total 51. 12 strikes → 300.
- **Fix:** `self.rolls[start + 1:start + 3]` (and pending if fewer than 2 exist).
- **Hints:** "Two strikes in a row."

### B2 · 10th-frame bonus rolls scored as an extra frame
- **Where:** `game.py::frame_totals`: iterates every parsed frame, not just the first 10.
- **Test:** 18 × 0, then X, 3, 4 → **17** (buggy 24).
- **Fix:** `frames[:FRAMES]`.
- **Why it hides:** all-spares (21 × 5) still gives 150, because the extra frame has one roll and is skipped as pending.
- **Hints:** "What happens to bonus rolls that form a complete open frame?"

### B3 · Handicap includes this week's games
- **Where:** `matches.py::_team_games`: extends the bowlers' history **before** computing the handicap.
- **Test:** history 150/161/170 (handicap 36); this week three 70s → each game counts 70 + 36 = **106** (buggy uses an average of 115, handicap 76).
- **Fix:** compute handicaps first, then append the games (or compute from a copy).
- **Hints:** "Which games should the average include?"

### B4 · Ties go to the home team
- **Where:** `matches.py::record_match`: `if h >= a`.
- **Test:** identical teams → each gets 2.0 points.
- **Fix:** `>`, `<`, else 0.5 each.
- **Hints:** "What does a tie earn?"

### B5 · Frames 1–9 can exceed 10 pins
- **Where:** `game.py::roll`: no check against the open frame's first roll.
- **Test:** rolls 5 then 6 → rejected.
- **Fix:** if the current frame (1–9) has one roll `r` and `r + pins > 10`, raise.
- **Hints:** "Try an impossible frame."

## Red herrings
- `render.symbols` (scorecard) is correct, including 10th-frame marks.
- `is_complete` is correct.
- Average floor division is per spec.

## Questions about the candidate's fixes (data structures)
- **B1/B2:** "You index into `self.rolls` from a frame's start. Why is a roll list (not frames) the better source of truth?" (Bonuses are roll-based; frames are a derived view. Recomputing frames each call is O(r) with r ≤ 21: trivial.)
- **B3:** "History is a list of every game ever: average is O(n) per call. How would you make it O(1)?" (Store running total + count per bowler. Then 'previous games only' means reading those two numbers before adding the week, so the bug becomes structurally less likely.)
- **Standings:** "`standings` recomputes from all results: O(matches). When would you keep a running table?" (Many reads; but corrections to past matches then need reversals.)
- **General:** "What's an invariant you'd assert on every recorded match?" (Points sum to 4.)

## Feature requests
1. **"Blind scores: if a bowler is absent, the team gets their average minus 10 pins for each game, with no handicap."** Strong answer: a placeholder entry in the match; the average comes from history; absences don't update history.
2. **"Live scoring: frame totals update after every roll and show pending frames."** Strong answer: `frame_totals` already returns None for pending; push events per roll; idempotency when a lane resends a roll.
3. **"Season high-game and high-series awards, with and without handicap."** Strong answer: track maxima incrementally per bowler; tie rules; which handicap applied that week (store it with the result).

## Scoring signals
- **Strong:** encodes all three spec examples **and** finds that only some fail; designs the X,3,4 tenth frame; spots that the handicap is computed after mutation.
- **Weak:** stays inside `game.py`; never records a match.
