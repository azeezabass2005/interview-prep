# NEWS-1101: Same story appears 3–4 times in the panel

**Type:** Bug · **Reporter:** News desk · **Priority:** High

## Description
The same article shows up several times because partners link it with different URLs:
- `https://www.partner.example/markets/fed-holds?utm_source=x`
- `https://partner.example/markets/fed-holds/`
- `HTTPS://Partner.example/markets/fed-holds#comments`

## Acceptance criteria
- All of the above are treated as one story (the first one ingested is kept).
- URLs that differ in meaningful query parameters (e.g. `?id=1` vs `?id=2`) stay separate stories.

## Out of scope
- Detecting the same story under different headlines.
