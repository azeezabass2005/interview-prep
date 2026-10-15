# 01 · Pot Luck: interviewer notes

Rebuilt from the workshop's example question (Nicole Zhu). Code: `potluck/`.

## Answers to give when the candidate asks (you are the PM)

| Topic | Answer |
|---|---|
| Matching | Positional, by index. `12345` vs `54321` = 1 match (the middle 3). Repeated digits count per position. |
| Rounding | Integer cents. Each winner gets the floor; leftover cents roll over. |
| Closure | Entries after `close()` must be rejected. |
| Snapshot | A closed draw must never change, even after the next draw starts. |
| Validation | Codes are always exactly 5 numeric characters, stored as strings. |
| Multiplicity | A participant may buy many entries; each entry is paid independently. |
| Tier cap | Each tier takes its % of the *pot at draw time*, capped at what is still unclaimed. Higher tiers go first. |
| Rollover | The rollover is added to the next draw's pot. |

If they don't ask: let them assume, but they should say "I'm assuming X and will add a test for it."

## Requirement map

| # | Requirement | Status |
|---|---|---|
| R1 | $10,000 seed + $5 per entry | implemented |
| R2 | Codes 00000–99999 | **bug**: no zero-padding |
| R3 | Pot computed at draw time, including rollover | **bug**: rollover never added |
| R4 | Positional matching | **bug**: set membership |
| R5 | Reverse-order tiers, 5-match first | **bug**: ascending order |
| R6 | Split within a tier | implemented (floor) |
| R7 | Leftover rolls over | computed but not carried (see R3) |
| R8 | Reject entries after close | **gap**: missing |
| R9 | Closed draw is immutable | **bug**: `start_next_draw` clears the shared list |

## Planted issues

| ID | Location | What is wrong | Minimal fix | Test that fails for one reason |
|---|---|---|---|---|
| B1 | `drawing.py::_generate_code` | `str(n)` drops leading zeros: 42 becomes `"42"` | `f"{n:0{CODE_LENGTH}d}"` | FakeRng → 42, assert `"00042"`. Also 99999 → `"99999"` |
| B2 | `matching.py::count_matches` | `digit in winning_code` is set membership, not positional | `sum(a == b for a, b in zip(entry, winning))` | `12345` vs `54321` → 1 |
| B3 | `payouts.py::build_payout_plan` | `sorted(winners_by_tier)` is ascending, so the 4-match tier is paid before the 5-match tier, which then only gets the remaining 60% | `sorted(..., reverse=True)` | One 5-match and one 4-match: 5-match gets 100%, 4-match gets 0 |
| B4 | `drawing.py::current_pot_cents` | `_rollover_cents` is stored by `settle` but never added | add `+ self._rollover_cents` (and reset it once consumed) | Draw 1 has no winners. Draw 2's pot = seed + rollover |
| B5 | `drawing.py::start_next_draw` / `close` | `Draw.entries` is the same list object, and `.clear()` wipes the closed draw | snapshot in `close` (`list(self._entries)`) and/or rebind `self._entries = []` | Close, start next draw, `settle(old_draw)` still pays |
| G1 | `drawing.py::add_entry` | No check that the draw is open | `if self._closed: raise RuntimeError` | add_entry after close raises |

**Red herring:** the floor division in the split is not a bug. It is the open rounding question. Good candidates point it out as an assumption, not a defect. If the agent calls it a bug, the candidate should push back.

**Subtle one:** once B4 is fixed, rollover must be *consumed*, not re-added every draw. Watch whether the candidate thinks about that.

## Workshop numbers (worked example)

Pot = 1,000,000 + 4×500 = 1,002,000¢. 40% = 400,800, which is 133,600 each for 3 winners. 5% = 50,100. Rollover = 551,100.

## High-signal prompts to listen for
- "Summarize SPEC.md into numbered requirements and list anything ambiguous. Don't look at the code yet."
- "Given requirement 2 (codes 00000–99999), point me to where codes are generated and stored. Don't change code."
- "List likely mismatches between the spec and the code, with file and function. Don't fix anything."
- "Write one test that forces the random source to return 42 and asserts '00042'."

## Follow-up questions to ask
- Why is `winners_by_tier` a dict of lists? What would you use for O(1) lookup by participant?
- Complexity of settling N entries? (O(N·L) to match, plus O(T) tiers.)
- How would you make the snapshot guarantee hold structurally? (Tuple / frozen dataclass.)
