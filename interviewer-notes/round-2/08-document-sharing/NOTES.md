# R2-08 · Vault (document sharing): Interviewer Guide

A ~650-line Python document service (no framework): ownership and sharing (ACL), public share links, cursor pagination,
cached previews, search and a body-size limit. Bugs are in access control, the data layer, caching and middleware. The candidate
picks one ticket; one ticket done properly with a test is a full pass. `web/` is context only.

## Ticket map

| Ticket | Area | Real root cause | Where | Trap |
|---|---|---|---|---|
| DOC-801 expired links work | Authentication / authorization | `open_link` checks revoked but never `expires_at` | `services/documents.py: open_link` | Deleting expired links in a job (still works until the job runs); comparing strings of different formats |
| DOC-805 search leaks titles | Data access / authorization | `search` filters by workspace and title but not by the `ACCESSIBLE` clause that the list uses (the `:user` parameter is passed but unused) | `repositories/documents.py: search` | Filtering results in Python after the query (works, but `LIMIT` then hides accessible matches); fixing in the handler |
| DOC-810 missing from list | Data access / pagination | Cursor holds only `updated_at`; the next page asks for `updated_at < cursor`, so documents with the **same** timestamp as the last row are skipped | `services/documents.py: encode/decode_cursor` + `repositories/documents.py: accessible_page` | Using `<=` (duplicates and possible infinite loop); offset pagination |
| DOC-815 stale preview | Caching | Preview cache key is `preview:{doc_id}`, so a new version hits the old entry; updates don't invalidate | `services/documents.py: preview` | Disabling the cache; invalidating in `update` only (works on one instance; versioned keys work everywhere) |
| DOC-820 huge upload | Middleware | `body_limit` trusts the `Content-Length` header; chunked bodies have none and a client can lie | `limits.py` | Rejecting requests without `Content-Length` (breaks legitimate chunked clients); checking in one handler only |

## PM answers
| Question | Answer |
|---|---|
| Should an expired link be 404 or 410? | Same as revoked: 404 with the same message (don't confirm the link existed). |
| Can search show "restricted document" placeholders? | No: nothing at all about unreadable documents. |
| Is the cursor format part of the API? | No, it's opaque; clients just send it back. You can change what's inside. |
| How fresh must previews be? | Always the current version. Old versions can stay in the cache until they expire. |
| What about requests without Content-Length? | Allowed, as long as the body is under 1 MB. |

## DOC-801 · link expiry
**Fix:** in `open_link`, treat `parse_iso(link["expires_at"]) <= now` like revoked (404, same message).
**Test:** 48-hour link; advance 47 h → 200; advance to 48 h → 404.

## DOC-805 · search access filter
**Fix:** add `AND {ACCESSIBLE}` to the search WHERE clause (the query already binds `:user`).
**Test:** Nadia's private "Project Falcon" and a "Project Kite" shared with Tom: Tom's search for "project" returns only Kite; Nadia sees
both. Strong: notices that the list already uses `ACCESSIBLE`, and says that every query returning document data must go through
it (or through a repository method that always applies it).

## DOC-810 · keyset cursor
**Fix:** encode `(updated_at, id)` in the cursor and query
`(d.updated_at < :after OR (d.updated_at = :after AND d.id < :after_id))`, matching the `ORDER BY updated_at DESC, id DESC`.
**Test:** 25 documents with the same timestamp → page 1 has 20, page 2 has 5, no duplicates, all 25 ids seen.

## DOC-815 · versioned cache key
**Fix:** `key = f"preview:{doc.id}:{doc.version}"`.
**Test:** preview v1, edit, preview → version 2 and the new words; preview again → rendered once for v2 (count `_render_preview` calls with
`mock.patch.object`, or check `cache.hits`).

## DOC-820 · enforce the real size
**Fix:** `if len(request.body) > max_bytes or declared > max_bytes: raise PayloadTooLarge(...)`.
**Test:** a 1.1 MB body with no `Content-Length` → 413; with `Content-Length: 100` → 413; a normal create still 201. Strong: says the
real protection belongs before the body is buffered (server/LB), which is why the ticket scopes it out.

## Red herrings
- `_readable` returns 404 (not 403) for unshared documents on purpose.
- `update_content`'s optimistic version check is correct.
- `PublicLinks` correctly makes only `/s/…` public.

## Questions about the candidate's fixes (data structures)
- "Why keyset pagination instead of OFFSET?" (Stable under inserts, O(log n) with the `(workspace_id, updated_at, id)` index; OFFSET
  re-reads skipped rows and shifts when rows are added.)
- "How does `ACCESSIBLE` perform with 1M documents?" (EXISTS per row on the `acl` primary key; an index on `acl(user_id, doc_id)` helps
  the "shared with me" side; or maintain a per-user accessible set.)
- "LRU vs FIFO eviction for previews?" (The cache evicts the oldest inserted; LRU keeps hot previews: OrderedDict move_to_end.)
- "Share link tokens are hashed in the DB. Why?" (A DB leak doesn't leak working links; lookup by hash is still a primary-key hit.)

## Feature requests
1. **"Watermark shared-link views with the viewer's email."** Strong: links become per-recipient (identity on the link), rendering at
   view time, cache key includes recipient, audit log.
2. **"Full-text search on content."** Strong: SQLite FTS5 or an external index; keep access filtering in the query; reindex on update
   asynchronously; consistency trade-offs.
3. **"Document version history."** Strong: append-only versions table, current pointer, diff on read, retention policy, previews per
   version (which the versioned cache key already supports).

## Scoring signals
- **Strong:** writes the attacker/edge test first (two users, identical timestamps, chunked body); compares with the code path that's
  already correct (list's ACCESSIBLE, revoked check); keeps the response shape.
- **Weak:** filters in Python after LIMIT; uses `<=` in the cursor; turns caching off; rejects all chunked requests.
