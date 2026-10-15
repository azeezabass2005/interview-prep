# FF-1703: Admins think flag changes "didn't save"

**Type:** Bug · **Reporter:** Product managers · **Priority:** Medium

## Description
A PM disables a flag in the admin page, which immediately re-evaluates it to show the result. It still says "on". Refreshing a few times
later shows "off". PMs keep toggling it back and forth.

## Acceptance criteria
- Set the flag cache TTL to 0 so changes are always visible.
- A change is visible immediately on the instance that made it.

## Out of scope
- Push-based invalidation across instances.
