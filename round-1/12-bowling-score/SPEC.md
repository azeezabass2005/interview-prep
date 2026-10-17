# Bowling Score

A bowling league scores games and runs weekly handicap matches between two bowlers. `bowling.py` holds the scoring and the league.

## Scoring a game

A game has **10 frames**. Input is the list of rolls (pins knocked down) so far.
- **Strike** (10 on the first roll of a frame): 10 + the next **two** rolls.
- **Spare** (10 over two rolls): 10 + the next **one** roll.
- Otherwise the frame scores its pins.
- In the 10th frame, a strike or spare earns bonus rolls (up to 3 rolls in that frame). Bonus rolls are not frames.
- Two rolls in a frame (frames 1–9) can't knock down more than 10 pins.

`frame_scores(rolls)` returns the **running total** after each frame **started**. If a frame's score can't be known yet (its rolls or
bonus rolls haven't happened), that frame and every later one are `None`.

## Handicap

- A bowler's **average** = their previous league games' scores, averaged and rounded down. No previous games → no handicap.
- **Handicap** = 90% of (200 − average), rounded down, **never negative**.
- A match uses the handicap from games **before** this match.

## Matches

Each bowler's total = game score + handicap. Higher total gets **2 points**; a tie gives **1 each**.

## Example

Rolls `10, 7 3, 9 0, 10, 0 8, 8 2, 0 6, 10, 10, 10 8 1` → final score **167**.
