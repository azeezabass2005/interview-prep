# ALR-505: One provider hiccup delays alerts by an hour

**Type:** Bug · **Priority:** High · **Reporter:** Product

## Description
When Textwire has a short blip (a few timeouts), the affected alerts arrive about an hour late, after the price has already moved
on. Textwire was back within seconds each time. The README says retries back off from 30 seconds.

## Acceptance criteria
- Retries follow the documented schedule: 30 s, 60 s, 120 s, … doubling, never more than 1 hour apart.
- The maximum number of attempts is unchanged.
