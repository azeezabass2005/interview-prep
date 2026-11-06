from ..models import Page, Report


def report_summary(r: Report) -> dict:
    return {"id": r.id, "title": r.title, "sector": r.sector, "summary": r.summary, "published_at": r.published_at,
            "status": r.status}


def report_full(r: Report) -> dict:
    return {**report_summary(r), "body": r.body, "analyst_id": r.analyst_id}


def page(p: Page) -> dict:
    return {"items": [report_summary(r) for r in p.items], "page": p.page, "page_size": p.page_size, "has_more": p.has_more}
