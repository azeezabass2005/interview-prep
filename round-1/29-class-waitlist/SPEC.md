# Class Waitlist

A fitness studio runs classes with a fixed number of spots. Members book a spot or join a waitlist; when a spot frees up, the waitlist
moves. `studio.py` handles bookings.

## Members

- **UNLIMITED** members book as many classes as they like.
- **PACK** members have class credits: booking a spot uses 1 credit; they need at least 1 credit to book or join a waitlist.

## Booking

- If there's a free spot the member is **BOOKED**, otherwise they join the **waitlist** (max **5** people; then refused).
- A member can't hold two places in the same class (booked or waitlisted).

## Cancelling

- Cancelling **12 hours or more** before the class starts is free; PACK members get their credit back.
- Cancelling **less than 12 hours** before: UNLIMITED members pay a **$10.00** fee; PACK members lose the credit.
- Leaving the waitlist is always free.

## Waitlist promotion

When a booked member cancels, the **first person on the waitlist** (first come, first served) is booked automatically (a PACK member
uses a credit) — **except in the last hour before the class**, when the spot is left open.

## Example

Capacity 1. Ana books, Ben joins the waitlist. Ana cancels 20 hours before → no fee, **Ben is booked**.
