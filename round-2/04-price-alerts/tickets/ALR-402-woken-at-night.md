# ALR-402: Users woken up at 2 a.m. despite quiet hours

**Type:** Bug · **Reporter:** Customer support · **Priority:** Medium

## Description
Users with quiet hours set to 22:00–07:00 get notifications in the middle of the night. Users with quiet hours 13:00–14:00 (lunch) say
it works for them.

## Steps to reproduce
1. User in `America/New_York`, quiet hours 22:00–07:00.
2. An alert fires at 02:00 New York time.
3. The delivery is due immediately and is sent.

## Acceptance criteria
- Deliveries created during quiet hours (including windows that span midnight) are held until the quiet period ends, in the user's time zone.
- Daytime windows (e.g. 13:00–14:00) keep working.

## Out of scope
- Letting users pick different quiet hours per weekday.
