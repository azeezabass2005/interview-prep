# R1-41 · News Feed: Interviewer Guide

The Round 1 version of Round 2 #11. One file, `feed.py` (~90 lines), with one passing test. **The spec example fails on the buggy code**
(muted spamwire appears, and the later Bloomberg copy wins because of B2/B5), giving several leads at once — watch whether the
candidate untangles them one at a time.

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Same headline 25 hours apart | Two stories: both shown. |
| Embargo at exactly now | Visible. |
| Follow and mute the same source | Muted wins. |
| Cursor format | (publish time, article id) of the last item. |
| Ties in dedupe (same time) | Lowest id kept (stable sort). |

## Code map
`normalise` · `add` · `follow` · `_matches` · `_visible` (filter, dedupe, sort) · `page` (cursor).

## Planted bugs (5)

### B1 · Mute only applies to followed sources
- **Where:** `_matches`.
- **Test:** muted source with a followed ticker → **not shown**.

### B2 · Latest copy kept
- **Where:** `_visible`: both branches assign `kept[key] = a` (the `else` should keep the first).
- **Test:** 09:00 Reuters + 10:00 Bloomberg same headline → **r1**.

### B3 · Cursor skips equal timestamps
- **Where:** `page`: compares only `published_at`.
- **Test:** three articles at 09:00, pages of 2 → **[a3, a2] then [a1]** (buggy second page empty).

### B4 · Embargo ignored
- **Where:** `_visible` ignores `now` (clue).
- **Test:** an article an hour in the future → **hidden**.

### B5 · Whitespace not collapsed
- **Where:** `normalise`.
- **Test:** "Fed holds rates" vs "  fed  HOLDS rates " → **one** article.

Hints: (1) "look at both branches of the dedupe `if`"; (2) "which parameter is never used?"

## Red herrings
- Sorting by (time, id) descending: correct.
- `next_cursor` only when the page is full: acceptable (PM: fine).

## Questions about the candidate's fixes (data structures)
- **`_visible` rebuilds the whole feed per page:** O(N log N). "At scale?" (Fan-out on write: per-user feed lists; or fan-out on read with per-ticker/per-source indexes merged via a heap (k-way merge) — O(k log s).)
- **Dedupe dict keyed by normalised headline:** "Near-duplicates ('Apple beats Q3 estimates')?" (Shingling / MinHash / SimHash; trade-offs.)
- **B3:** "Why tuple comparison for the cursor?" (Total order: no ties.) "Why not offset pagination?" (Inserts shift offsets → skips/repeats.)
- **Sets for prefs:** "Why sets?" (O(1) membership; intersection with tickers.)

## Feature requests
1. **"Breaking news: high-priority articles pinned to the top for 30 minutes."** Strong answer: two-tier sort key; pinned expiry; cursor still stable.
2. **"Per-user relevance ranking instead of pure time."** Strong answer: score function; cursor must encode the score; pagination stability issues.
3. **"Read state: hide articles the user has opened."** Strong answer: per-user set of read ids (bounded); filter in `_visible`.

## Scoring signals
- **Strong:** separates the example's failures into single-cause tests; paginates with ties.
- **Weak:** patches until the example passes without isolating causes.
