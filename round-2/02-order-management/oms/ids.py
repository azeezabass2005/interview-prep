import itertools
import uuid

_counter = itertools.count(1)


def new_order_id() -> str:
    return f"ORD{next(_counter):06d}-{uuid.uuid4().hex[:6]}"
