# Fitness Class Booking

A gym's app lets members book spots in classes. When a class is full, members join a **waitlist** and are promoted automatically
when someone cancels. The code in `classes/` implements the rules below. Members report being skipped on the waitlist and charged unfairly.

## Rules

- Each class has a **capacity** and a **start time**.
- **Booking:** if there's space the member is **BOOKED**; otherwise they join the **waitlist** (**WAITLISTED**).
  The waitlist holds at most **10** members; beyond that, booking is rejected.
- A member can't hold more than one place in a class (booked **or** waitlisted).
- **Waitlist order:** **premium** members are ahead of standard members. Within each group, first come, first served.
- **Cancelling a booking** frees the spot, and the **first member on the waitlist is promoted** to BOOKED automatically,
  **except in the last hour before the class starts**. Then the spot stays open and nobody is promoted.
- **Late-cancel fee:** cancelling a **booking** less than **12 hours** before the class costs **$10**. Leaving the waitlist is always free.

## Example

Capacity 1. Ana books (BOOKED). Sam (standard) joins the waitlist, then Pia (premium) joins the waitlist.
Waitlist order: **Pia, Sam**. Ana cancels 20 hours before class: no fee, **Pia is promoted**.

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model classes, bookings and the waitlist, and which data structure you'd use for the waitlist.
3. Outline booking/cancellation behaviour and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
