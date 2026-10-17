# R1-50 · Document Versioning: Interviewer Guide

The Round 1 version of Round 2 #20. One file, `docs.py` (~85 lines), with one passing test. **The spec example fails on the buggy
code** (B1: Ana's stale save succeeds; B5: readers see v2).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Lock holder saving with a stale base | Still a conflict. |
| Restore a deleted version | Error. |
| Publish a version, then it's the oldest | Never deleted. |
| Lock at exactly 30 minutes | Expired. |
| Read with nothing published | `None`. |

## Code map
`_add_version` (numbering, retention) · `create` · `lock` · `save` · `restore` · `publish` · `read`.

## Planted bugs (5)

### B1 · `base_version` ignored
- **Where:** `save` (parameter unused: clue).
- **Test:** two edits from v1 → the second raises a conflict.

### B2 · Restore overwrites the latest version
- **Where:** `restore` writes into `doc.latest`.
- **Test:** restore v1 → new **v3** with "a"; v2 still "b".

### B3 · Retention deletes the published version
- **Where:** `_add_version`.
- **Test:** max 3, v1 published, save v2–v4 → versions **[1, 3, 4]**.

### B4 · Expired locks still block saves
- **Where:** `save` (`lock` checks expiry; `save` doesn't — compare them).
- **Test:** Ana's lock expired; Ben saves → **v2**.

### B5 · Readers see the latest draft
- **Where:** `read` ignores `published`.
- **Test:** publish v1, save v2 → read **v1**.

Hints: (1) "compare `lock` and `save`"; (2) "the example is a story: write all three steps".

## Red herrings
- Version numbers keep increasing after deletions: correct (`latest` counter).
- `create` rejects duplicates: correct.

## Questions about the candidate's fixes (data structures)
- **Versions in a dict keyed by number:** "Why a dict and not a list?" (Deletions leave gaps; O(1) lookup by number.) "`min(doc.versions)` each deletion: O(n). Better?" (A deque of version numbers in order; skip the published one.)
- **B1:** "What's the server-side equivalent in a database?" (`UPDATE … WHERE version = :base` and check rows affected; or a unique (doc, version) constraint.)
- **Storing full content per version:** "100 versions of a 5 MB note?" (Store diffs / content-addressed blobs; dedupe identical versions.)
- **Locks vs optimistic concurrency:** "Why have both?" (Locks for long edits with humans; versions to catch anything that slips through.)

## Feature requests
1. **"Three-way merge instead of rejecting conflicts."** Strong answer: base, mine, theirs; `difflib` or a merge library; conflict markers when overlapping.
2. **"Diff between two versions for reviewers."** Strong answer: `difflib.unified_diff`; line-level stats; cost for large docs.
3. **"Scheduled publishing at 06:00 before market open."** Strong answer: publish job with a time; publishes a specific version; cancellation.

## Scoring signals
- **Strong:** turns the example into a test; compares lock vs save; checks history after restore.
- **Weak:** only linear single-author saves.
