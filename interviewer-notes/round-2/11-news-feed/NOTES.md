# R2-11 · News Feed Aggregator: interviewer notes

~330 lines. Mostly **correctness of data rules** (canonicalisation, cursors, units) and one ticket whose AC proposes infrastructure
for a normalisation bug.

## Ticket map

| Ticket | Real root cause | Where | Trap |
|---|---|---|---|
| NEWS-1101 duplicates | `canonical_url` drops tracking params and the fragment, but doesn't lower-case scheme/host, strip `www.`, or strip the trailing `/` | `services/urls.py::canonical_url` | Lower-casing the **path** too (paths are case-sensitive, so it would merge distinct stories) |
| NEWS-1102 skipped stories | **Offset** pagination: new stories shift every offset | `services/feed.py::page`, `repositories/stories.py::newest` | Snapshotting the feed per user (heavy). Fix: keyset cursor `(published_at, story_id)` = "strictly older than the last story seen" |
| NEWS-1103 old stories on top | `age_hours = total_seconds() / 86400` (days, not hours), so decay is 24× too slow | `services/ranking.py::score` | Tuning `HALF_LIFE_HOURS` to compensate (two wrongs) |
| NEWS-1104 tag search | Tags stored and compared case-sensitively (`Fed` ≠ `fed`) | `repositories/stories.py::insert/with_tag` | **AC proposes a nightly index rebuild.** There's no index cache; the data is simply not normalised. Ideal fix: normalise on write **and** compare case-insensitively on read (handles existing rows without a migration) |

## NEWS-1102 in depth
**Invariant:** for a fixed cursor, the next page is the `limit` stories strictly after the cursor in `(published_at DESC, story_id DESC)`
order. That's independent of inserts at the head. Cursor encoding: `"<published_at>|<story_id>"` (opaque to clients). Test: page 1, insert
2 newer stories, page 2 must be exactly the next 4 older ones.
Ask: "What about a story ingested late with an *old* `published_at`?" It could land behind the cursor and never be seen. That's acceptable
or not depending on product. A good thing to raise as a remaining risk.

## Out-of-scope smells
- `_is_tracking` treats any key starting with `ref` as tracking (`reference=…` would be dropped). Spec says `ref` exactly.
- `_hydrate` does an N+1 query for tags. Performance, not correctness. Mention only.

## Strong prompts
- "Given these three URLs from the ticket, show me what `canonical_url` returns for each, step by step. Don't change code."
- "Explain what offset 4 means before and after two new stories arrive."
