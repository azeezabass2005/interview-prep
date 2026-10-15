# Warehouse Inventory (FIFO Costing)

A warehouse values stock and computes cost of goods sold (COGS) using **FIFO**: the oldest stock is assumed to ship first.
The code in `inventory/` implements the rules below. The month-end numbers don't reconcile.

## Rules

- **Receipts** add a cost **layer**: SKU, quantity, unit cost, received date.
- **Shipments** consume a SKU's layers **oldest first**. COGS = Σ (units taken from each layer × that layer's unit cost).
  A layer that is partly consumed keeps the rest of its units.
- A shipment larger than the SKU's on-hand quantity is **rejected** and changes nothing.
- Each SKU's layers are independent. Shipping one SKU never touches another SKU's layers.
- **Returns** reference a shipment. Returned units go back into stock as a **new (newest) layer** at that shipment's
  **average unit cost** (COGS ÷ units shipped, to 4 decimal places). You can't return more than was shipped.
- **Valuation** of a SKU = Σ remaining units × unit cost.

## Example

Receive 100 @ $2.00 (Jan 1) and 50 @ $2.50 (Jan 5). Ship 120 → COGS = 100 × 2.00 + 20 × 2.50 = **$250.00**.
Remaining: 30 @ $2.50 = $75.00. Return 10 units of that shipment → new layer 10 @ $2.0833 → valuation **$95.83**.

## Candidate questions

1. Identify anything in the rules that must be clarified before implementation.
2. Explain how you would model layers, shipments and returns, and which data structure fits FIFO.
3. Outline the COGS calculation and the tests you would want.
4. Identify bugs or issues and fix them.

```
python -m unittest discover -s tests -v
```
