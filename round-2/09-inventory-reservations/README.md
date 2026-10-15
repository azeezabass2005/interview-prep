# Inventory Reservation Service

Backs the online store for corporate hardware (keyboards, cables, docking stations…). When a shopper adds an item to their cart the
service **reserves** stock for 15 minutes; on checkout the reservation becomes a sale; abandoned reservations are released by a
**sweeper** that runs every minute. Some products are **bundles** made of other SKUs. Several API instances share one database.

Pick one ticket from `tickets/`, make a bounded change and prove it. One ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

## Layout

```
stock/api/handlers.py              InventoryApi
stock/services/reservations.py     reserve / release / sweep_expired
stock/services/checkout.py         confirm a cart
stock/services/availability.py     available units for SKUs and bundles
stock/services/reports.py          low-stock report for purchasing
stock/repositories/*.py            skus, bundle_components, reservations
stock/db.py, clock.py, errors.py, models.py, config.py
```

## Rules

- `available = on_hand − reserved`. It must never be negative.
- A reservation holds units for **15 minutes**. Expired reservations are released **once** by the sweeper.
- Checkout turns a cart's active reservations into sales: `on_hand −= qty` and `reserved −= qty`.
- A **bundle** has no stock of its own. It's made of components, each with a quantity per bundle. Bundle availability is how many
  complete bundles the components can make. Reserving N bundles reserves `N × qty` of each component, all or nothing.
- The **low-stock report** lists every SKU whose `on_hand` is **at or below its own `reorder_point`**.
