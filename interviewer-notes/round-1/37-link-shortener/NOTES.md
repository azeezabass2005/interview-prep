# R1-37 · Link Shortener: Interviewer Guide

The Round 1 version of Round 2 #07. One file, `shortener.py` (~90 lines), with one passing test. The spec example passes on the buggy
code (code 1 encodes the same either way; one user).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Alias stored as typed or lowercased? | Lowercased. |
| Same URL, same user, but with an alias | Always a new link (aliases are explicit). |
| Expired links count as taken aliases? | Yes. |
| Deleted link, same user shortens again | New link. |
| Code collision with an alias (`000001` as an alias)? | Out of scope. |

## Code map
`encode` · `shorten` (url → alias rules → dedupe → generated code) · `resolve` · `delete`.

## Planted bugs (5)

### B1 · Aliases are case-sensitive
- **Where:** `shorten`: checks `alias in self.links` with the original case.
- **Test:** `Promo` then `promo` → refused.

### B2 · Reserved words allowed
- **Where:** `shorten`; `RESERVED` unused (clue).
- **Test:** alias `admin` → refused.

### B3 · Dedupe across users
- **Where:** `shorten` loop ignores `owner`.
- **Test:** Ana and Ben shorten the same URL → Ben's link is **Ben's**.

### B4 · Expiry boundary
- **Where:** `resolve`: `>`.
- **Test:** resolve exactly at `expires_at` → **410**.

### B5 · Base 62 digits reversed
- **Where:** `encode`.
- **Test:** `encode(62)` → **`000010`** (buggy `000001`, colliding with link 1).

Hints: (1) "the spec gives you two encoding examples — test both"; (2) "which constants are never used?"

## Red herrings
- `resolve` falls back to the lowercase key: correct (and hides B1 for resolution).
- Delete by owner only: correct.

## Questions about the candidate's fixes (data structures)
- **B3:** "The dedupe loop is O(links). Better?" (Dict (owner, url) → code: O(1).)
- **Codes from a counter:** "Downsides?" (Guessable/enumerable; reveals volume. Alternatives: random codes with collision check; hashids.) "Collision probability for random 6-char base62?" (62⁶ ≈ 57B; birthday bound: about 280k links for a 50% chance of at least one collision, so check and retry.)
- **Multiple servers:** "Two servers increment the counter." (Central sequence; or ranges allocated per server; or random codes + unique constraint.)
- **Click counting at scale:** "One row per click?" (Batch counters in memory, flush periodically; approximate counts.)

## Feature requests
1. **"QR codes and UTM parameters appended per channel."** Strong answer: variants of a link; resolution appends parameters; stats per channel.
2. **"Rate limit link creation per user."** Strong answer: token bucket per user; 429.
3. **"Clicks per day for the last 30 days."** Strong answer: dict (code, day) → count; or a time-series store; time zones.

## Scoring signals
- **Strong:** uses the spec's encoding examples as tests; two-user dedupe test; checks case for aliases.
- **Weak:** only round-trips one link.
