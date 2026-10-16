# Fitness Studio Booking

A fitness studio sells memberships and runs classes with limited spots. Members book spots; when a class is full they join a **waitlist**
and may be promoted automatically. The repository contains the booking service.

## Memberships

- **UNLIMITED:** book any number of classes. **PREMIUM** is UNLIMITED with waitlist priority.
- **PACK:** a pack of class **credits**. Booking a spot uses 1 credit. Joining a waitlist uses no credit; the credit is used if and when the
  member is promoted.

## Booking and waitlist

- If a class has space, the member is **BOOKED**; otherwise they join the waitlist (at most **10** people), unless they're a PACK member with
  no credits left (rejected).
- A member can hold only one place in a class (booked or waitlisted).
- **Waitlist order:** PREMIUM members first; within each group, first come, first served.

## Cancellation

- Cancelling a booking **12 hours or more** before the class is free (PACK members get their credit back).
- Cancelling **less than 12 hours** before: UNLIMITED/PREMIUM members pay a **$10** late fee; PACK members **forfeit the credit** (no fee).
- Leaving the waitlist is always free.

## Promotion

When a booked spot frees up, the first eligible person on the waitlist is promoted automatically, **except in the last hour before the
class**. A PACK member with no credits left is skipped (they stay on the waitlist). Promoted members leave the waitlist.

## Example

Capacity 1. Ana (UNLIMITED) books. Sam (UNLIMITED) and Pia (PREMIUM) join the waitlist in that order → waitlist **Pia, Sam**.
Ana cancels 20 h before → no fee, **Pia is promoted**.
