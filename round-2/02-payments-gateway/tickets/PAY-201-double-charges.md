# PAY-201: Customers charged twice for one order

**Type:** Bug · **Priority:** Critical · **Reporter:** Merchant Support

## Description
Bean & Co reports 14 customers charged twice last Thursday. Each of them has **one** payment in our system and in their order
system, but two charges for the same amount on their card statement, a few seconds apart. Thursday afternoon was when Paystream
had elevated latency (many requests to them took more than 8 seconds).

## Steps to reproduce
1. Paystream accepts a charge but the response doesn't arrive before our timeout.
2. We retry, and Paystream creates a second charge.

## Acceptance criteria
- A payment never results in more than one charge at Paystream, including when we retry after a timeout.
- Refunds get the same protection.
- A test shows a timed-out first attempt followed by a retry can't create a second charge.

## Out of scope
- Refunding the duplicate charges from Thursday (Support is doing it manually).
