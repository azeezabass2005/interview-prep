# R1-01 · Pot Luck: Interviewer Guide

Rebuilt and extended from the workshop's own Round 1 example (Nicole Zhu). ~450 lines in `potluck/`. One passing test exists.
**The spec's worked example passes on the buggy code.** The candidate has to derive edge cases from the rules to find anything.

## Session plan (60 min)
| Time | What happens |
|---|---|
| 0–5 | Resume + one past problem |
| 5–15 | Candidate reads SPEC.md, summarises it, asks clarifying questions (answer from the PM table) |
| 15–20 | Candidate maps the code with the agent (expect: api → services → store, payouts/matching helpers) |
| 20–45 | Bug hunt: test → fail → explain → minimal fix → re-run. Expect 3–5 bugs found |
| 45–55 | Data-structure questions on their fixes + one feature request (discussion, maybe partial code) |
| 55–60 | Wrap-up: remaining risks, what they'd do next |

## PM answers
| Question | Answer |
|---|---|
| Is matching positional? Repeated digits? | Positional, digit by digit. `12345` vs `54321` = 1 match (the 3). `11111` vs `11234` = 2. |
| Rounding when a split leaves cents | Round down per winner; leftover cents roll over (as the spec says). |
| Are entries rejected after close? | Yes: buying requires an open draw. |
| Can a draw's entries change after closing? | No: the closed draw is a snapshot. |
| Codes as strings or ints? | Always 5-character strings, leading zeros kept. |
| Can one participant win several times? | Yes: each entry is paid independently. |
| Is the 10-entry limit per draw or lifetime? | Per draw, counting only active entries. Cancelled entries free up a slot. |
| Does a cancelled entry count in the pot? | No: it's refunded. |
| Duplicate codes in one draw? | Allowed; each entry is its own ticket. |

## Code map
| Module | Responsibility |
|---|---|
| `api.py` | HTTP-shaped facade: status code + body |
| `app.py` | Wiring (`build_app(rng, clock)`), the seam for deterministic tests |
| `services/participants.py` | Registration, e-mail uniqueness (correct) |
| `services/entries.py` | Buy / cancel entries, per-draw limit |
| `services/draws.py` | Open / close / settle lifecycle, pot calculation |
| `services/payouts.py` | Tier allocation |
| `matching.py`, `codes.py` | Match counting, code generation |
| `store.py` | In-memory store with indexes by draw and by participant |
| `services/statements.py` | Participant statement and draw summary (correct) |

## Planted bugs (5)

### B1 · Codes lose leading zeros
- **Where:** `codes.py::CodeGenerator.next_code`. `str(value)` turns 42 into `"42"`.
- **Spec line:** "random 5-digit code from 00000 to 99999".
- **Test:** scripted RNG returns 42 → entry code `"00042"`; also 0 → `"00000"` and 99999 → `"99999"`.
- **Fix:** `f"{value:0{CODE_LENGTH}d}"`.
- **Knock-on:** an unpadded code fed to positional matching would misalign digits. Ask what happens to `"42"` vs `"00042"`.
- **Hints:** (1) "What does the spec say about the code range's lower end?" (2) "What does `str(42)` give you?"

### B2 · Matching isn't positional
- **Where:** `matching.py::match_count`. It uses a multiset intersection (`Counter & Counter`): shared digits regardless of position.
- **Why it hides:** every example in the spec has the same answer either way.
- **Test:** `54321` vs `12345` → 1 match (pays nothing; buggy code says 5 and pays the whole pot). Also `11111` vs `11234` → 2.
- **Fix:** `sum(a == b for a, b in zip(entry_code, winning_code))`.
- **Hints:** (1) "Try a code with the same digits in a different order." (2) "What does Counter intersection count?"

### B3 · Tiers paid lowest first
- **Where:** `services/payouts.py::build_settlement`. `sorted(TIER_SHARES)` is ascending.
- **Spec line:** "paid from the highest tier down… If 5-match winners take 100%, lower tiers get nothing."
- **Test:** one 5-match and one 4-match entry → the 5-match entry gets the whole pot, the 4-match entry gets 0 (buggy: 4-match gets 40%, 5-match gets the remaining 60%).
- **Fix:** `sorted(TIER_SHARES, reverse=True)`.
- **Hints:** (1) "Build a draw where the 5-match tier and another tier both have winners." (2) "In what order does the loop visit tiers?"

### B4 · Cancelled entries still grow the pot
- **Where:** `services/draws.py::pot_for`. It counts **all** entries for the draw, not active ones. (Note `close_draw` correctly snapshots active entries only, so the payout set is right but the pot is inflated.)
- **Test:** buy 3, cancel 1, close → pot = 1,000,000 + 2 × 500 = 1,001,000 cents.
- **Fix:** `entries_for_draw(draw.draw_id, active_only=True)`.
- **Hints:** (1) "What happens to the pot when someone cancels?" (2) "Compare how `pot_for` and `close_draw` select entries."

### B5 · Entry limit counts other draws
- **Where:** `services/entries.py::active_count`. It counts the participant's active entries across **all** draws. Entries stay `ACTIVE` after their draw settles, so a regular player is locked out of every future draw.
- **Test:** buy 10 in draw 1, settle, open draw 2, buy 1 → succeeds (buggy: 422). Also: 10 in one draw → 11th rejected (must still hold).
- **Fix:** count entries where `e.draw_id == draw.draw_id and e.status == ACTIVE` (pass the draw in).
- **Hints:** (1) "Play two consecutive draws with a heavy player." (2) "Which entries does `active_count` look at?"

## Red herrings (correct; good candidates verify rather than "fix")
- Rollover carry-over in `open_draw` is correct.
- Leftover cents from floor division go to rollover. That's by spec.
- E-mail uniqueness is case-insensitive (correct).
- `statements.spent_cents` counts only active entries: correct, because cancellations are refunded.

## Questions about the candidate's fixes (data structures)
- **B2:** "Your fix zips two strings: what's the cost? (O(L).) Why was `Counter` the wrong abstraction here, and when *would* a multiset be right?" (An anagram-style rule.)
- **B4/B5:** "`entries_for_draw` builds a list and filters it every call. Over a draw's lifetime, how expensive is the limit check?" (O(entries of that participant), or O(draw entries) if done naively.) "What index would make the per-draw active count O(1)?" (Maintain `active_count[(draw_id, participant_id)]`, updated on buy and cancel. Trade-off: one more piece of state that must stay consistent.)
- **B3:** "TIER_SHARES is a dict. Why sort it every settlement? Alternatives?" (A pre-sorted tuple of (tier, share); an OrderedDict. Tiny n, so it's about clarity, not speed.)
- **Store:** "`entries_by_draw` is a dict of lists. Why lists and not sets?" (Insertion order = purchase order; deterministic payouts. A set loses order and costs more memory.) "Cancel does a dict lookup: O(1). What would it cost without the `entries` dict?"

## General complexity questions
- Settlement: matching N entries of length L is O(N·L) time, O(N) extra space for the groups.
- "If a draw had 50 million entries, how would you find the 5-match winners quickly?" Index entries by code: `dict[code] → [entry ids]` gives exact matches in O(1). For 4-match: for each of 5 positions, look up the code with that position wildcarded. Precompute `dict[(pos, code-with-wildcard)]`: O(5N) space, O(5 × 10) lookups.
- `latest_draw` uses `max(self.draws)`: O(D) per call. Better: keep the latest id.

## Feature requests (pick one after the bugs)
1. **"Let participants choose their own code instead of a random one; still allow random 'quick picks'."**
   Strong answer: validation (exactly 5 digits as a string); a per-draw `dict[code] → list[entry_id]` to report popularity; whether duplicates are allowed (ask PM: yes); tests for leading zeros; the API change is backwards compatible (optional `code` field).
2. **"Guarantee a minimum jackpot: if the pot is below $15,000 at close, the sponsor tops it up, and the top-up is not rolled over."**
   Strong answer: where the pot is computed (one place: `pot_for`); separate `sponsor_topup_cents` field so rollover excludes it; tests for both sides of the threshold; explain the accounting invariant (awarded + rollover + unreturned top-up = pot).
3. **"Entries purchased in the last 10 minutes before close count double in the 2-match tier."**
   Strong answer: question the requirement (how is "double" split?); model it as a weight on the entry; the payout split becomes weighted (largest-remainder rounding); state the new invariant that tier totals still never exceed entitlement.

## Scoring signals
- **Strong:** turns the spec example into a test first, notices it passes, then deliberately designs edge cases (order of tiers, permutations, cancellations, multiple draws). Uses the scripted RNG seam. One bug per test.
- **Weak:** asks the agent to "find all bugs and fix them"; accepts a "fix" to floor division (red herring); never tests across two draws (misses B5).

## Model prompts
- "Summarise SPEC.md as numbered, testable requirements and list ambiguities. Don't look at the code yet."
- "For requirement 'pot = seed + $5 × active entries + rollover', show me every line that computes or uses the pot. Don't change anything."
- "Write one test that scripts the RNG to return 42 for an entry and asserts the code is '00042'."
