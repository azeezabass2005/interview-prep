# Price Alerts

Users set alerts on stock prices ("tell me when ABC goes above $100"). Price ticks stream in; when an alert fires, a notification is
scheduled. `alerts.py` evaluates alerts and schedules notifications.

## Alerts

- An alert has a user, symbol, condition (**ABOVE** or **BELOW**) and threshold. It's **one-shot** (default) or **recurring**.
- An alert fires when the price **crosses** the threshold: for ABOVE, the price moves from below the threshold to **at or above** it
  (BELOW is the mirror image: from above to at or below).
- An alert created while the condition already holds (e.g. ABOVE 100 created when the last price is 105) does **not** fire until the
  price has gone back below and crosses again.
- One-shot alerts are switched off after firing. Recurring alerts fire again each time the price crosses again.

## Notifications

- **Quiet hours:** each user has quiet hours in their time zone (default **22:00–07:00**, crossing midnight). A notification created during
  quiet hours is delivered at the **end** of the quiet period; otherwise immediately.
- **Daily cap:** each user gets at most **3** notifications per UTC day; further ones are recorded as SUPPRESSED. Other users are unaffected.

## Example

Last price 95. Ana creates ABOVE 100. Tick 99 → nothing. Tick 101 → fires; it's 14:00 in London → delivered immediately. Tick 102 →
nothing (one-shot, already fired).
