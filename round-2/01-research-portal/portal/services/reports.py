from ..auth import Principal
from ..clock import iso
from ..errors import Forbidden, NotFound, ValidationError
from ..models import Page, Report
from ..schema import SECTORS

MAX_PAGE_SIZE = 50


class ReportService:
    def __init__(self, reports, entitlements, orgs, cache, clock, ids):
        self._reports = reports
        self._entitlements = entitlements
        self._orgs = orgs
        self._cache = cache
        self._clock = clock
        self._ids = ids

    def _is_internal(self, principal: Principal) -> bool:
        org = self._orgs.get(principal.org_id)
        return org is not None and org.kind == "internal"

    def readable_sectors(self, principal: Principal) -> set[str]:
        if self._is_internal(principal):
            return set(SECTORS)
        return self._entitlements.sectors_for(principal.org_id, self._clock.now().date().isoformat())

    def list_reports(self, principal: Principal, sector: str | None, page: int, page_size: int) -> Page:
        if page < 1 or not 1 <= page_size <= MAX_PAGE_SIZE:
            raise ValidationError(f"page must be >= 1 and page_size between 1 and {MAX_PAGE_SIZE}")
        if sector is not None and sector not in SECTORS:
            raise ValidationError(f"unknown sector {sector}")
        key = f"reports:{sector or 'all'}:{page}:{page_size}"
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        sectors = self.readable_sectors(principal)
        if sector is not None:
            sectors = sectors & {sector}
        rows = self._reports.published(sorted(sectors), limit=page_size + 1, offset=(page - 1) * page_size)
        result = Page(rows, page, page_size, has_more=len(rows) > page_size)
        self._cache.set(key, result)
        return result

    def read_report(self, principal: Principal, report_id: str) -> Report:
        report = self._reports.get(report_id)
        if report is None or (report.status != "published" and not self._is_internal(principal)):
            raise NotFound("report not found")
        if report.sector not in self.readable_sectors(principal):
            raise Forbidden("your firm is not entitled to this sector")
        self._reports.record_read(report.id, principal.user_id, iso(self._clock.now()))
        return report

    def create_draft(self, principal: Principal, title: str, sector: str, summary: str, body: str) -> Report:
        principal.require_role("analyst")
        if sector not in SECTORS:
            raise ValidationError(f"unknown sector {sector}")
        if not title.strip() or not summary.strip():
            raise ValidationError("title and summary are required")
        report = Report(self._ids.new("rpt"), title.strip(), sector, principal.user_id, "draft", summary.strip(), body,
                        iso(self._clock.now()), None)
        self._reports.insert(report)
        return report

    def publish(self, principal: Principal, report_id: str) -> Report:
        principal.require_role("analyst", "editor")
        report = self._reports.get(report_id)
        if report is None:
            raise NotFound("report not found")
        if report.status != "draft":
            raise ValidationError(f"cannot publish a {report.status} report")
        self._reports.set_status(report.id, "published", iso(self._clock.now()))
        self._cache.delete_prefix("reports:")
        return self._reports.get(report.id)

    def withdraw(self, principal: Principal, report_id: str) -> Report:
        principal.require_role("editor")
        report = self._reports.get(report_id)
        if report is None:
            raise NotFound("report not found")
        self._reports.set_status(report.id, "withdrawn", report.published_at)
        self._cache.delete_prefix("reports:")
        return self._reports.get(report.id)

    def stats(self, principal: Principal, report_id: str) -> dict:
        if not self._is_internal(principal):
            raise Forbidden("internal users only")
        if self._reports.get(report_id) is None:
            raise NotFound("report not found")
        return self._reports.read_stats(report_id)
