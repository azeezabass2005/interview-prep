# ALR-401: One alert sends dozens of notifications

**Type:** Bug · **Reporter:** Mobile app support · **Priority:** High

## Description
A user set "IBM above 200". IBM traded around 200.50 for an hour and the user got a notification on **every tick**, 140 in total.
Users are uninstalling the app.

## Steps to reproduce
1. Alert: IBM ABOVE 200.
2. Ticks: 200.10, 200.40, 200.20, 199.95, 200.30.
3. Five deliveries are enqueued.

## Acceptance criteria
- An alert fires once when its threshold is reached, then stays quiet.
- It fires again only after the price has moved back below `threshold × 0.995` and then reached the threshold again.
- Ticks for the example above produce **one** delivery (199.95 is not far enough below 200 to re-arm).

## Out of scope
- Changing the re-arm percentage.
