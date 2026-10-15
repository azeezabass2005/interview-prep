# CAL-TICKET-vip-scoring: CEO requests rank below vendor pitches

**Type:** Bug · **Reporter:** Office of the CEO · **Priority:** High

## Description
Requests from the CEO keep landing at the bottom of the queue, below external vendor pitches. We think the VIP weight (50) is simply too
low compared with the urgency weights. The CEO's assistant marks most requests `normal`.

## Steps to reproduce
1. Submit a `normal` request from `CEO@bloomberg.example` (that's how the assistant's mail client sends it).
2. Submit a `high` request from `sales@vendor.example`.
3. Inspect scores: the CEO request scores **15**; the vendor request scores **30**.

## Acceptance criteria
- Raise the VIP sender weight from 50 to 80 so VIP requests always outrank external ones.
- A `normal` request from the CEO scores at least 60.

## Out of scope
- Changing urgency weights.
