# DOC-2002: Search finds notes by text that was removed

**Type:** Bug (compliance) · **Reporter:** Compliance · **Priority:** High

## Description
An analyst removed a client's name from a note. Searching for that name still returns the note, which compliance considers a leak.

## Acceptance criteria
- Search matches only the latest version of each document.

## Out of scope
- Purging old versions.
