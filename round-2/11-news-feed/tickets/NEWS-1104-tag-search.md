# NEWS-1104: Tag search misses tagged stories

**Type:** Bug · **Reporter:** Economics team · **Priority:** Medium

## Description
Searching the tag `fed` returns some Fed stories but not others. We think the search index is out of date and needs a nightly rebuild job.
The missing stories were tagged `Fed` or `FED` by partners.

## Acceptance criteria
- Add a nightly job that rebuilds the tag index.
- Searching `fed` returns stories tagged `Fed`, `FED` or `fed`.

## Out of scope
- Tag synonyms (e.g. `FOMC`).
