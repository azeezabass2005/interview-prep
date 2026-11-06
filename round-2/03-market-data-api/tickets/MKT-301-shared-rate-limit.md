# MKT-301: Pro customers get 429s far below their plan limit

**Type:** Bug · **Priority:** High · **Reporter:** Customer Success

## Description
Birch Capital (pro plan, 600 requests/minute) gets `429 Too Many Requests` after a few dozen requests in some minutes, and
sometimes their very first request of a minute is rejected. Alder Partners (basic plan) reported the same thing this morning, at
the same times. It's worst at the market open, when lots of customers are active. Our logs show Birch never came close to 600.

## Acceptance criteria
- Each customer's requests count only against that customer's own limit, based on their plan.
- Busy customers can't use up anyone else's allowance.
- Requests without a valid token are still rejected (401).

## Notes
All traffic reaches the API through the load balancer.
