from .models import RETAIL, Offering


def allocation_report(offering: Offering) -> dict:
    allocated = sum(offering.allocations.values())
    retail = sum(v for k, v in offering.allocations.items() if offering.orders[k].category == RETAIL)
    return {"offered": offering.shares, "allocated": allocated, "retained_by_issuer": offering.shares - allocated,
            "retail": retail, "institutional": allocated - retail,
            "proceeds": str(offering.final_price * allocated) if offering.final_price else None}
