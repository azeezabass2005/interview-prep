# MD-303: Consolidated quote shows bid above ask

**Type:** Bug · **Reporter:** Smart order router team · **Priority:** High

## Description
`GET /consolidated/{symbol}` sometimes returns a best bid **higher** than the best ask (a crossed market), which makes the router think
there's free money. It happens mostly for symbols where one venue stopped quoting a while ago.

## Steps to reproduce
1. Venue `ARCA` quotes XYZ 101.00 / 101.05 at 14:00:00.
2. Venue `BATS` quotes XYZ 100.00 / 100.02 at 14:00:20.
3. At 14:00:21 the consolidated quote is bid 101.00 / ask 100.02.

## Acceptance criteria
- Venue quotes older than `VENUE_MAX_AGE_S` are ignored, as documented.
- Best bid = highest bid and best ask = lowest ask among the remaining venues.

## Out of scope
- Venue fee adjustments.
