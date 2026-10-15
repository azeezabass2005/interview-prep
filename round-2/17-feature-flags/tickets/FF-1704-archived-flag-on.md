# FF-1704: Archived flag still returns its old value

**Type:** Bug · **Reporter:** Platform team · **Priority:** Medium

## Description
We archived `beta-export` (which was 100% on) and expected callers to fall back to their default (`False`). Callers still get `True`.

## Acceptance criteria
- Archived flags evaluate to the caller's default, like unknown flags.

## Out of scope
- Deleting archived flags from the database.
