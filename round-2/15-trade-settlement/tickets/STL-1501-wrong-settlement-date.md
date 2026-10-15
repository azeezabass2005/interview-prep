# STL-1501: Settlement dates wrong around weekends and holidays

**Type:** Bug · **Reporter:** Fixed income operations · **Priority:** High

## Description
Corporate bond trades done on Thursday 2 July 2026 got a settlement date of Monday 6 July. Friday 3 July is a market holiday, so the custodian
expects Tuesday 7 July. Friday trades in corporate bonds also settle a day early (Monday instead of Tuesday).

We think it's a time-zone problem: trade timestamps are in UTC and the market is in New York.

## Acceptance criteria
- Convert trade timestamps to New York time before computing the settlement date.
- Thursday 2 July 2026 corporate bond trade settles Tuesday 7 July 2026.

## Out of scope
- Non-US calendars.
