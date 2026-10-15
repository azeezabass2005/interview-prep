# DOC-2001: Co-author's edits silently lost

**Type:** Bug · **Reporter:** Equity research · **Priority:** Critical

## Description
Two analysts edited the same note. Both saves succeeded and both were told "saved as version 5". The note now has two version 5s, and the
editor shows only one of them; the other analyst's paragraph is gone. We expected the second save to be rejected so the editor could merge.

## Acceptance criteria
- A save whose `base_version` isn't the latest is rejected with 409 and stores nothing, including when both saves arrive at the same time.
- Version numbers are unique per document.

## Out of scope
- Automatic merging.
