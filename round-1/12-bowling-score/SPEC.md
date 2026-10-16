# Bowling League Scoring

A bowling centre runs a weekly handicap league. Each week two teams meet; every bowler bowls a **series of 3 games**. The software scores
games from individual rolls, keeps bowlers' averages, applies handicaps and awards team points. The repository contains it.

## Scoring a game

- 10 frames. In each frame a bowler has up to two rolls to knock down 10 pins.
- **Open frame:** pins knocked down. **Spare** (10 in two rolls): 10 + the next roll. **Strike** (10 on the first roll, frame ends):
  10 + the next two rolls, whichever frames they fall in.
- **10th frame:** a strike earns two bonus rolls, a spare one. Bonus rolls only count as the 10th frame's bonus; they're never frames of their own.
- **Validation:** each roll is 0–10 pins; in frames 1–9 the two rolls can't total more than 10; no rolls after the game is complete.
- A game is complete after the 10th frame (including any bonus rolls).

## Averages and handicap

- A bowler's **average** is the total pins of all their **previous** league games (before this week's series) divided by the number of
  games, **rounded down**. A bowler with no previous games has no average and a handicap of 0.
- **Handicap** per game = **90% of (200 − average)**, rounded down, never negative. It stays the same for all 3 games of the week.

## Team points (per match)

- For each of the 3 games, each team's total = Σ (bowler's game score + handicap). The higher total wins **1 point**; a tie gives each team **½ point**.
- The **series** (all 3 games combined, with handicap) is worth another **1 point**, with ties split the same way.
- So each match awards exactly 4 points.

## Examples

| Rolls | Score |
|---|---|
| 12 strikes | 300 |
| 21 × 5 (all spares) | 150 |
| X, X, 5, 3, then 14 × 0 | 51 |

A bowler with previous games 150, 161, 170 has average 160 → handicap ⌊0.9 × 40⌋ = **36**.
