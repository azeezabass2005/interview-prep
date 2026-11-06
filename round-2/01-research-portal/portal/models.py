from dataclasses import dataclass


@dataclass
class Org:
    id: str
    name: str
    kind: str


@dataclass
class User:
    id: str
    org_id: str
    email: str
    name: str
    digest_enabled: bool
    last_digest_at: str | None


@dataclass
class Report:
    id: str
    title: str
    sector: str
    analyst_id: str
    status: str
    summary: str
    body: str
    created_at: str
    published_at: str | None


@dataclass
class Page:
    items: list
    page: int
    page_size: int
    has_more: bool
