# RES-110: The last report on each page shows up again on the next page

**Type:** Bug · **Priority:** Medium · **Reporter:** Web team

## Description
With more than one page of research, the web app's list shows 21 rows on a 20-per-page view, and the 21st row is repeated as the
first row of page 2. QA also noticed page 2 of a 2-page list sometimes says there are more pages when there aren't.

## Steps to reproduce
1. 25 published reports in an entitled sector.
2. `GET /reports?page=1&page_size=20` returns 21 items; `GET /reports?page=2&page_size=20` starts with the 21st again.

## Acceptance criteria
- A page never has more than `page_size` items, and no report appears on two pages.
- `has_more` is true exactly when a later page has items.

## Out of scope
- Switching to cursor-based pagination (planned, RES-140).
