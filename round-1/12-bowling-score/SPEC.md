# Bowling Scorekeeper

A bowling alley's lane monitors show a live scorecard. The code in `bowling/` records rolls and computes the score.
Bowlers keep complaining that the screen is wrong.

## Rules

- A game has **10 frames**. In each frame the bowler has up to **two rolls** to knock down **10 pins**.
- **Open frame:** fewer than 10 pins in two rolls. The frame scores the pins knocked down.
- **Spare:** all 10 pins in two rolls. The frame scores 10 **plus the next roll**.
- **Strike:** all 10 pins on the first roll (the frame ends). The frame scores 10 **plus the next two rolls**,
  whichever frames those rolls fall in.
- **10th frame:** a strike earns **two** bonus rolls; a spare earns **one**. Bonus rolls only count as the 10th frame's
  bonus. They're never frames of their own.
- **Validation:** a roll is 0–10 pins. In frames 1–9 the two rolls of a frame can't total more than 10.
  Rolling after the game is complete is an error.
- **Scorecard:** shows a running total per frame. A frame whose bonus rolls haven't been thrown yet shows **no total**
  (`None`), and so does every frame after it.

## Examples

| Rolls | Score |
|---|---|
| 20 × 0 | 0 |
| 12 strikes | 300 |
| 21 × 5 (all spares) | 150 |
| X, X, 5, 3, then 14 × 0 | 25 + 18 + 8 = **51** |

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model rolls and frames.
3. Outline the scoring algorithm and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
