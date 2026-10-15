# FF-1702: User override ignored for UK users

**Type:** Bug · **Reporter:** Support engineering · **Priority:** Medium

## Description
We turned `new-dashboard` **off** for one UK client user (override) because it breaks their screen reader. They still get the new dashboard.
There's a segment rule "country == GB → on". Overrides for non-UK users work.

## Acceptance criteria
- User overrides take precedence over segment rules and rollout, as documented.

## Out of scope
- A UI for overrides.
