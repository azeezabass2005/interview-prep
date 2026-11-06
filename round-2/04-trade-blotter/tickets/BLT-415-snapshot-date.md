# BLT-415: Friday's end-of-day snapshot is labelled Saturday

**Type:** Bug · **Priority:** High · **Reporter:** Risk Reporting

## Description
Monday's regulatory position report failed: there's no snapshot for Friday 2026-06-05, but there is one for Saturday 2026-06-06,
with Friday's closing positions. The same thing happens every day; we only noticed because there's no Saturday report to look
for. The snapshot job runs at 21:30 New York time.

## Acceptance criteria
- The end-of-day snapshot is labelled with the New York business date on which it was taken.
- Trade dates are unaffected (they're correct today).

## Out of scope
- Daylight saving changes: the offset is configured (`config.py`) and Ops changes it twice a year.
