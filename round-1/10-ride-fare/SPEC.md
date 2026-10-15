# Ride Fare Calculator

A ride-hailing app charges riders when a trip ends and sometimes when they cancel. The code in `fare/` implements the pricing rules
below. Support has a pile of fare disputes.

## Trip fare

1. **Metered subtotal** = $2.50 base + **$1.20 per mile** + **$0.30 per minute**.
   Distance is measured to the hundredth of a mile; **any started minute counts** as a full minute.
2. **Surge:** the metered subtotal is multiplied by the surge multiplier **shown to the rider when they requested the ride**
   (it's locked in, even if surge changes during the trip). Surge is **capped at 3.0×**.
3. **Booking fee:** a flat **$2.00**, never surged.
4. **Minimum fare:** surged subtotal + booking fee is at least **$7.00**.
5. **Tolls** are passed through at cost, **after** the minimum fare is applied.
6. The total is rounded half-up to the cent.

## Cancellation fee

A rider who cancels more than **2 minutes** after a driver was assigned pays **$5.00**, unless the driver is running more
than **5 minutes** late against the ETA given at assignment (and hasn't arrived). Then it's free.

## Example

5.3 miles, 14 min 20 s, locked surge 1.5×, $3.00 toll:
`(2.50 + 6.36 + 15 × 0.30) = 13.36 → × 1.5 = 20.04 → + 2.00 = 22.04 → + 3.00 toll = $25.04`.

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model trips, quotes and charges.
3. Outline the fare calculation and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
