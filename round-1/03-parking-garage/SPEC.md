# Garage Billing

A city parking garage issues a ticket on entry and charges on exit. The code in `garage/`
implements the billing rules below. It doesn't get all of them right.

## Rules

- **Grace period:** stays of **30 minutes or less** are free.
- **Hourly rate:** otherwise **$4 per hour or part thereof**, counted from entry time.
- **Daily maximum:** at most **$24 per 24-hour period**, counted from entry time. A stay of 26 hours
  is one capped 24-hour period plus 2 more hours.
- **Early bird:** enter between **06:00 and 09:00** and leave the **same day before 19:00**,
  and you pay a flat **$12**. Early bird is a deal: it must never cost more than the normal rate.
- **Monthly pass holders:** park free when they *enter* on a weekday (Mon–Fri). Weekend entries pay the normal rate.
- **Lost ticket:** **$50** flat, replacing every other rule.
- A ticket is issued on entry, closed on exit, and can be closed **only once**.

## Examples

| Entry | Exit | Charge |
|---|---|---|
| Tue 10:00 | Tue 10:25 | $0 (grace) |
| Tue 10:00 | Tue 12:31 | $12 (3 started hours) |
| Tue 07:15 | Tue 17:30 | $12 (early bird) |
| Mon 10:00 | Tue 12:00 | $32 ($24 cap for the first 24 h, then 2 h × $4) |

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model tickets, stays, and charges.
3. Outline the fee calculation and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
