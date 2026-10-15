# LNK-702: Click counts lower than our web analytics

**Type:** Bug · **Reporter:** Research distribution · **Priority:** Medium

## Description
For a link shared in a newsletter, our web analytics recorded 10,412 landings but the link's `clicks` shows 9,870. The `click_events`
table has 10,409 rows for the link. The gap grows during bursts (newsletter send time).

## Acceptance criteria
- After N redirects of a link (concurrent or not), `clicks == N`.

## Out of scope
- Bot filtering.
