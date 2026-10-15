# Group Tab

A bill-splitting app divides a restaurant bill among friends. One person pays the restaurant;
everyone else pays that person back. The code in `tab/` implements the rules below. Users say the numbers don't always add up.

## Rules

1. **Items:** each item has a price and the people who shared it. An item is split **equally** among its sharers.
   A person's **subtotal** is the sum of their item shares.
2. **Coupon:** an optional fixed amount off the bill, applied **before tax**.
3. **Tax:** **8.875%** of the (discounted) subtotal, rounded half-up to the cent.
4. **Tip:** a percentage of the **pre-tax, discounted subtotal** (default **18%**), rounded half-up to the cent.
   Parties of **6 or more people** are charged an automatic **20%** gratuity instead.
5. **Each person's share** of the final total (subtotal − coupon + tax + tip) is **proportional to their subtotal**.
6. **No cent may be lost or invented:** shares must add up to the total exactly. Leftover cents from any split go
   one cent at a time to people in **alphabetical order**.
7. **Settle up:** everyone except the payer sends the payer one transfer for their share.

## Example

alice, bob, carol. Pizza $30.00 (all three), Wine $20.00 (alice, bob), Salad $12.00 (carol). alice pays.

| | alice | bob | carol | total |
|---|---|---|---|---|
| subtotal | 20.00 | 20.00 | 22.00 | 62.00 |
| tax (8.875%) | | | | 5.50 |
| tip (18% of 62.00) | | | | 11.16 |
| **total** | | | | **78.66** |

bob and carol each send alice their share. The three shares add up to exactly $78.66.

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model items, people and the breakdown.
3. Outline the calculation and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
