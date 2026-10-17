# R1-01 · Pot Luck: Interviewer Guide

The workshop's own example. One file, `potluck.py` (~125 lines), with one passing test (pot size). **The spec example passes on the
buggy code**: every bug needs a boundary or a scenario the example doesn't cover.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt (test → fix) · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Code 42 | Stored and shown as `00042`. |
| Two 5-match winners | Split 100% equally. |
| Tier with nothing left | Winners get $0.00; it isn't an error. |
| Rounding | Always down to the cent; leftover cents roll over. |
| Cancel after close | Not allowed. |
| Limit of 10 | Active entries only. |

## Code map
`register` · `open_draw` · `buy` (limit) · `cancel` · `close` (pot, winning code) · `matches` · `settle` (tiers, split, rollover).

## Planted bugs (5)

### B1 · Codes lose leading zeros
- **Where:** `_new_code`: `str(randint(...))`.
- **Test:** scripted RNG returns 42 → code `"00042"`.
- **Fix:** `f"{n:05d}"`.

### B2 · Matching isn't positional
- **Where:** `matches`: set intersection counts shared digits anywhere.
- **Hides because:** every example row gives the same count either way.
- **Test:** entry `54321` vs winning `12345` → 1 match, no payout (buggy: 5 matches, the whole pot).
- **Fix:** `sum(a == b for a, b in zip(code, winning))`.

### B3 · Tier not capped by what's left
- **Where:** `settle`: `amount = draw.pot * share`.
- **Test:** a 5-match and a 4-match winner → the 4-match winner gets $0, and the rollover is $0 (buggy: pays out 140%).
- **Fix:** `min(pot * share, remaining)`.

### B4 · Cancelled entries count toward the limit
- **Where:** `buy`: `held` counts every entry.
- **Test:** buy 10, cancel 1, buy 1 → allowed.

### B5 · Split rounds half-up
- **Where:** `settle`: `ROUND_HALF_UP`.
- **Test:** 6 entries (pot $10,030), three 3-match winners → $668.66 each, rollover $8,024.02 (buggy $668.67).

Hints: (1) read the spec sentence back; (2) "what input makes the example's numbers come out differently?"

## Red herrings
- E-mail uniqueness (lower-cased): correct.
- The pot counts only active entries: correct.
- Rollover = pot − paid: correct, once B3 and B5 are fixed.

## Questions about the candidate's fixes (data structures)
- **B2:** "Why did a set give the right answer for the example? What does a set lose?" (Position and multiplicity.) "Complexity of your fix?" (O(5).)
- **B4:** "`buy` scans every entry in the draw to count a participant's: O(E) per purchase. What would you keep instead?" (A dict participant → active count, updated on buy and cancel. Trade-off: two sources of truth.)
- **`settle`:** "You group entries into a dict by match count. Why a dict and not sorting?" (O(E) vs O(E log E); tiers are fixed.)
- **`entry not in draw.entries`** in `cancel` is a list scan, O(E). "Fix?" (Store `draw_number` on the entry: O(1).)
- **Money:** "Why Decimal, not float?" (Exact cents; `0.1 + 0.2`.)

## Feature requests
1. **"Let a participant pick their own code (lucky numbers)."** Strong answer: validate 5 digits as a string; duplicates allowed; RNG only as fallback; same matching.
2. **"Cap a single winner's payout at $50,000 and send the excess to charity."** Strong answer: where in `settle` (after the split); excess no longer rolls over; a test at exactly the cap.
3. **"Allow buying entries for the next three draws in advance."** Strong answer: entries tied to a draw number, not "current"; pot counted at that draw's close; refunds if a draw never opens.

## Scoring signals
- **Strong:** builds a scripted RNG test double early; looks for an input where the example would change (finds B2); tests the cap with a 5-match winner.
- **Weak:** turns the example into a test, sees it pass, and stops.
