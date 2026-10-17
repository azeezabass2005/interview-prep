# Document Versioning

Analysts write research notes in a shared editor that keeps every version. `docs.py` stores documents, versions, publishing and locks.

## Versions

- Creating a document makes **version 1**. Each save makes a new version (2, 3, …) with the author and content.
- **Optimistic concurrency:** a save says which version it was based on. If that's not the latest version, the save is rejected as a
  **conflict** (so nobody silently overwrites someone else's work).
- **Restore** an old version by creating a **new** version with its content; history is never rewritten.

## Publishing

Any version can be **published**. Readers always see the **published** version (or nothing if none is published), never unpublished drafts.

## Locks

An editor can lock a document for **30 minutes**. While the lock is active, only the lock holder can save. Expired locks are ignored.

## Retention

A document keeps at most N versions (default 20). When a save goes over the limit, the **oldest versions are deleted first**, but the
**published version is never deleted**.

## Example

Ana creates the note (v1) and publishes it. Ben edits from v1 → v2. Ana also edits from v1 → **conflict**. Readers still see **v1**.
