# R2-20 · Research Document Store: interviewer notes

~345 lines. DOC-2001 is **optimistic concurrency**: the cleanest store-owned fix in the whole set is a single UNIQUE constraint, because
"version = base_version + 1" turns both the stale-save check and the race into one insert conflict.

## Ticket map

| Ticket | Real root cause | Where | Trap |
|---|---|---|---|
| DOC-2001 lost edits | `save` ignores `base_version` and computes `max(version) + 1`; no UNIQUE on (doc_id, version), so concurrent saves get the same number | `services/editing.py::save`, `db.py` | Comparing `base_version` with `latest` in Python *and* stopping there (still check-then-insert). Accept: UNIQUE(doc_id, version) + insert `base_version + 1` → IntegrityError → 409. (Or a conditional insert inside `BEGIN IMMEDIATE`) |
| DOC-2002 search old text | `search` joins **all** versions | `repositories/versions.py::search` | Deleting old versions (README: immutable). Fix: restrict to each document's max version |
| DOC-2003 restore does nothing | `restore` saves `latest.content` instead of `target.content` | `services/editing.py::restore` | **AC says delete the versions after k.** That violates immutability (README) and destroys audit history. Restore = new version with old content |
| DOC-2004 autosave noise | The no-op check compares against the **first** version, not the latest | `services/editing.py::save` | Comparing against *any* previous version (then reverting to an older text wouldn't create a version, which is also wrong) |

## DOC-2001 in depth
**Invariant:** (doc_id, version) is unique, and a save succeeds only if it was based on the latest version.
Deterministic test: two `EditingService` instances, both saving with `base_version = 1`; pause the first two `max_version` calls on
`Barrier(2)` (buggy path). Exactly one gets version 2; the other gets `VersionConflict`; history is `[1, 2]`. Also a sequential stale save →
409. Ask: "What does the client do on 409?" (Fetch latest, merge, retry: out of scope, but they should know.)

## Interplay worth noticing
DOC-2003's buggy restore **looks like it works** in one case: once DOC-2004 is fixed, saving the latest content is a no-op, so restore
returns the latest version number and nothing changes. A candidate who fixes 2004 first may think 2003 is "fine". The test must assert
**content**, not just success.

## Out-of-scope smells
- Search uses `LIKE '%text%'` (no index; injection-safe because parameterised). Mention performance only.
- Deleting a document doesn't check ownership.

## Strong prompts
- "What does `base_version` do in `save` today? Show me every line that reads it. Don't change code."
- "Which single schema change would make two saves from the same base impossible to both succeed?"
