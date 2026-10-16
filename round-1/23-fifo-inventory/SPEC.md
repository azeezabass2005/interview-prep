# Warehouse Inventory (FIFO Costing)

A distributor stocks SKUs in several warehouses and values inventory with **FIFO**: the oldest units are assumed to leave first. The
repository contains receiving, shipping, transfers, returns and valuation.

## Cost layers

- **Receiving** creates a cost layer in a warehouse: SKU, quantity, unit cost, received date.
- Each (SKU, warehouse) has its own layers; nothing in one warehouse affects another.

## Shipments

- A shipment from a warehouse consumes that warehouse's layers **oldest received first** (ties: the order they were created).
  A layer that is partly consumed keeps its remaining units.
- COGS = Σ units taken × the layer's unit cost.
- A shipment larger than the available quantity is **rejected and changes nothing**.

## Transfers

Moving units between warehouses takes them from the source **FIFO** and creates layers in the destination with the **same unit costs
and the same received dates** as the layers they came from (a transfer never changes cost or age).

## Returns

A customer return references a shipment. Returned units come back into the shipment's warehouse as a new layer dated the **return date**,
at the shipment's **average unit cost** (COGS ÷ units, 4 decimal places). You can't return more than was shipped.

## Valuation

Value of a SKU in a warehouse = Σ remaining units × unit cost, rounded half-up to the cent.

## Example

Warehouse NJ: receive 100 @ $2.00 (Jan 1) and 50 @ $2.50 (Jan 5). Ship 120 → COGS = 100 × 2.00 + 20 × 2.50 = **$250.00**.
Remaining 30 @ $2.50 = $75.00. Return 10 → new layer 10 @ $2.0833 → valuation **$95.83**.
