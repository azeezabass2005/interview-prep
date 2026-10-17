# Parking Garage

A city garage has ticket gates at the entrance and exit. Visitors take a ticket, may get it **validated** by a shop, pay at a machine
and leave. Permit holders park for free. `garage.py` runs the gates and the pay machines.

## Spaces

The garage has **100 spaces**, of which **10 are reserved for permit holders**: a visitor may enter only while fewer than 90 cars are
inside. Permit holders may enter while there's any space. A plate can't be inside twice.

## Charges (visitors)

- Stays of **15 minutes or less** are free.
- Otherwise **$3.00 per started hour**, counted from entry.
- **Daily maximum:** at most **$20.00 per 24-hour period** from entry. (A 26-hour stay is one full day plus 2 started hours.)
- **Validation:** a shop can validate a ticket **once**. A validation takes **2 hours off the parked time** before charges are worked out
  (the 15-minute check uses the real time).

## Paying and leaving

Pay at a machine before leaving. After paying you have **15 minutes** to exit; otherwise the gate refuses and you pay again for the
extra time. A stay that costs nothing needs no payment.

## Example

Visitor parks 3 h 10 min → 4 started hours → **$12.00**. With a validation: 1 h 10 min → **$6.00**.
