# FIFO Inventory

A distributor keeps stock in several warehouses and values it **first in, first out**. `inventory.py` tracks lots, shipments,
transfers and returns.

## Lots

Each receipt creates a **lot**: quantity, unit cost, received date. Stock of a SKU in a warehouse is the list of its lots.

## Shipping

- Shipping consumes the **oldest lots first** (by received date). Cost of goods sold (COGS) = Σ consumed quantity × lot cost.
- A shipment is **all or nothing**: if the warehouse doesn't have enough, nothing is shipped and the stock is unchanged.

## Transfers

Moving stock between warehouses takes the oldest lots from the source. The moved quantities keep their **original cost and received
date**, so they stay in the right FIFO position at the destination.

## Returns

A customer can return part of a shipment. Returned units go back into the shipping warehouse as a new lot dated the return date, at the
**average unit cost of that shipment**. You can't return more than was shipped.

## Valuation and reordering

- Value = Σ quantity × unit cost of the lots in a warehouse.
- Each (warehouse, SKU) can have a reorder point. When a shipment leaves on-hand quantity **at or below** it, a reorder suggestion is recorded.

## Example

Receive 100 @ $2.00 (1 Mar) and 100 @ $2.50 (5 Mar). Ship 150 → COGS 100 × 2.00 + 50 × 2.50 = **$325.00**. 50 left, valued **$125.00**.
