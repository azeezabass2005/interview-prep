# Inventory Reservations

An online shop reserves stock while a customer's cart is open, so two customers can't buy the last item. `stock.py` tracks stock,
cart reservations and checkouts.

## Stock

Each SKU has an **on-hand** quantity. **Available** = on hand − active (unexpired) reservations.

## Reservations

- A cart reserves a quantity of a SKU if that much is available. Reservations **expire 15 minutes** after they were made; expired
  reservations no longer hold stock.
- Reserving the same SKU again for the same cart **replaces** the cart's quantity (the cart wants 5, not 3 + 5) and restarts the 15 minutes.
- Carts can release a reservation.

## Checkout

- Checkout sells everything the cart has reserved: on hand goes down and the cart's reservations are **removed**.
- It's **all or nothing**: if any of the cart's reservations has expired, the checkout fails and **nothing** changes.

## Low-stock alerts

When available stock of a SKU drops to **5 or fewer**, record one low-stock alert for it. Don't record another until the SKU has been
restocked above 5.

## Other operations

- `cart(cart, now)` shows a cart's reservations with seconds left and whether each has expired.
- `sweep(now)` deletes expired reservations and returns how many.
- `adjust(sku, counted, now)` sets on hand to a stock-take count (never negative) and returns the difference; low-stock rules apply as usual.

## Example

On hand 10. Cart A reserves 4 → available 6. Cart B reserves 1 → available 5 → **low-stock alert**. Cart A checks out → on hand 6,
available 5.
