# DOC-2004: Version history full of identical autosaves

**Type:** Bug · **Reporter:** Editor team · **Priority:** Low

## Description
Leaving the editor open creates a new version every autosave even when nothing changed. One note has 1,800 versions, almost all identical.
It only happens on notes that have been edited at least once after creation.

## Acceptance criteria
- Saving content identical to the latest version doesn't create a version and returns the latest version number.

## Out of scope
- Cleaning up existing duplicates.
