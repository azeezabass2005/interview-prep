# DOC-2003: "Restore this version" doesn't restore anything

**Type:** Bug · **Reporter:** Equity research · **Priority:** Medium

## Description
Clicking "Restore" on an old version reports success but the note's content doesn't change.

## Acceptance criteria
- Restoring version k rolls the document back by deleting all versions after k.
- After restoring, the latest content equals version k's content.

## Out of scope
- Restoring deleted documents.
