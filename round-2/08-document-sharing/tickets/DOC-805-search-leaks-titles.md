# DOC-805: Search shows titles of documents I can't open

**Type:** Security · **Priority:** Critical · **Reporter:** Compliance (policy C-12 breach)

## Description
An analyst searched for "project" and saw "Project Falcon – Acquisition of Northwind (CONFIDENTIAL)" in the results. Clicking it
says "document not found", but the deal name itself is inside-information: the analyst isn't on that deal team. Search returns
every document in the workspace whose title matches, regardless of who it belongs to.

## Acceptance criteria
- Search only returns documents the user can read (owned or shared with them).
- Results for documents the user can read are unchanged.
