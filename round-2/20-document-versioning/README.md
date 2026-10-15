# Research Document Store

Analysts write research notes in a web editor. Every save creates an **immutable version**; the editor autosaves every few seconds.
Several API instances share one database.

Pick one ticket from `tickets/`, make a bounded change and prove it. One ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

## Layout

```
docstore/api/handlers.py           DocsApi
docstore/services/editing.py       EditingService: create, save, restore
docstore/services/search.py        full-text search (substring, for now)
docstore/services/checksums.py     content hashing
docstore/repositories/*.py         documents, versions
docstore/db.py, clock.py, errors.py, models.py
```

## Rules

- Versions are numbered 1, 2, 3, … per document and are **never modified or deleted**.
- **Optimistic concurrency:** a save sends `base_version`, the version the editor started from. If someone else saved since then
  (`base_version` isn't the latest), the save is rejected with **409** and nothing is stored. The client then merges and retries.
- Saving content **identical to the latest version** is a no-op that returns the latest version number (autosave).
- **Restore** of version *k* creates a **new** latest version whose content equals version *k*.
- **Search** matches against each document's **latest** version only. Deleted documents never appear.
