# DOC-810: Imported documents missing from the list

**Type:** Bug · **Priority:** High · **Reporter:** Deals team

## Description
We imported 60 documents from the old system for the Falcon deal team. The import stamps them all with the same time. The web
app's list shows 20, then "Load more" shows nothing and the list ends. Search finds the missing ones, so they exist.
Documents created normally (seconds apart) page fine.

## Acceptance criteria
- Paging through the list shows every accessible document exactly once, even when many share the same timestamp.
- Order stays newest first; cursors stay opaque to clients.
