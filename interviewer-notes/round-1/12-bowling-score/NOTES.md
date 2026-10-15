# 12 · Bowling Scorekeeper: interviewer notes

Code: `bowling/game.py`. Shape: lookahead bonuses (rolls vs frames), a special final stage, incremental/partial state, validation and lifecycle.

## PM answers

| Topic | Answer |
|---|---|
| Bonus = next rolls or next frame? | Next **rolls**, crossing frame boundaries (X, X, 5 → first frame 25). |
| Pending totals | `None` for the pending frame and all later frames. |
| 10th-frame validation (e.g. X, 5, 6) | Nice to have, out of scope for this round. Only frames 1–9 must be validated. |
| Negative pins | Invalid (already handled). |
| Score of an incomplete game | Last known running total. |
| Fouls / splits | Out of scope. |

## Planted issues

| ID | Location | What is wrong | Fix | Failing test |
|---|---|---|---|---|
| B1 | `frame_scores` | Strike bonus is "the next frame's rolls", so X, X gets only 10 bonus | `sum(self.rolls[start+1:start+3])` | X, X, 5, 3, 14×0 = 51 |
| B2 | `frame_scores` | Iterates over **all** parsed frames: 10th-frame bonus rolls become frames 11 and 12 | `frames[:FRAMES]` | 21 × 5 = 150 (buggy: 155) |
| B3 | `roll` | No check that a frame's two rolls total ≤ 10 | validate against the open frame's first roll in frames 1–9 | 5 then 6 raises |
| B4 | `roll` | Can roll after the game is complete | `if self.is_complete(): raise` | 21st roll after 20 zeros raises |
| B5 | `frame_scores` | A pending strike/spare shows a number | append `None` once bonus rolls are missing | after a single strike: `[None]` |

The perfect game (300) fails on the original code for **two** reasons (B1 and B2). Expect strong candidates to notice when one fix gets them to 290-something but not 300.

**Red herring:** `_frames` itself is fine. It parses a sequence of rolls; the 10th-frame semantics belong in scoring. Watch whether the candidate (or the agent) rewrites `_frames` and breaks `is_complete`.

## Follow-ups
- What's the cleanest invariant? ("Exactly 10 frames scored; bonuses are roll-indexed.")
- Why store rolls rather than frames? (Single source of truth; frames are derived.)
