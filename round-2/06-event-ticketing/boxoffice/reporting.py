from .repositories.orders import OrderRepository


def sales_summary(orders: OrderRepository, event_id: str) -> dict:
    count, total = orders.sold_for_event(event_id)
    return {"event_id": event_id, "orders": count, "revenue_cents": total}
