import base64
import hashlib
import json
import secrets
from datetime import timedelta

from ..auth import Principal
from ..cache import TTLCache
from ..clock import iso, parse_iso
from ..config import MAX_LINK_HOURS, PAGE_SIZE, PREVIEW_CACHE_SECONDS
from ..errors import Conflict, Forbidden, NotFound, ValidationError
from ..models import Document


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def encode_cursor(doc: Document) -> str:
    return base64.urlsafe_b64encode(json.dumps({"updated_at": doc.updated_at}).encode()).decode()


def decode_cursor(cursor: str) -> str:
    try:
        return json.loads(base64.urlsafe_b64decode(cursor.encode()))["updated_at"]
    except (ValueError, KeyError) as e:
        raise ValidationError("invalid cursor") from e


class DocumentService:
    def __init__(self, docs, links, clock, ids, logger):
        self._docs = docs
        self._links = links
        self._clock = clock
        self._ids = ids
        self._logger = logger
        self._previews = TTLCache(clock, PREVIEW_CACHE_SECONDS)

    def _readable(self, principal: Principal, doc_id: str) -> Document:
        doc = self._docs.get(doc_id)
        if doc is None or doc.workspace_id != principal.org_id:
            raise NotFound("document not found")
        if doc.owner_id != principal.user_id and self._docs.permission(doc.id, principal.user_id) is None:
            raise NotFound("document not found")
        return doc

    def create(self, principal: Principal, title: str, content: str) -> Document:
        if not title.strip():
            raise ValidationError("title is required")
        now = iso(self._clock.now())
        doc = Document(self._ids.new("doc"), principal.org_id, principal.user_id, title.strip(), content, 1, now, now)
        self._docs.add(doc)
        return doc

    def get(self, principal: Principal, doc_id: str) -> Document:
        return self._readable(principal, doc_id)

    def update(self, principal: Principal, doc_id: str, content: str, version: int) -> Document:
        doc = self._readable(principal, doc_id)
        if doc.owner_id != principal.user_id and self._docs.permission(doc.id, principal.user_id) != "edit":
            raise Forbidden("you can view this document but not edit it")
        if not self._docs.update_content(doc.id, content, version, iso(self._clock.now())):
            raise Conflict("the document changed since you opened it; reload and merge")
        return self._docs.get(doc.id)

    def page(self, principal: Principal, cursor: str | None, limit: int = PAGE_SIZE) -> tuple[list[Document], str | None]:
        after = decode_cursor(cursor) if cursor else None
        docs = self._docs.accessible_page(principal.org_id, principal.user_id, after, limit + 1)
        has_more = len(docs) > limit
        docs = docs[:limit]
        return docs, (encode_cursor(docs[-1]) if has_more and docs else None)

    def search(self, principal: Principal, text: str) -> list[Document]:
        if len(text.strip()) < 2:
            raise ValidationError("search needs at least 2 characters")
        return self._docs.search(principal.org_id, principal.user_id, text.strip())

    def preview(self, principal: Principal, doc_id: str) -> dict:
        doc = self._readable(principal, doc_id)
        key = f"preview:{doc.id}"
        cached = self._previews.get(key)
        if cached is None:
            cached = self._render_preview(doc)
            self._previews.set(key, cached)
        return cached

    def _render_preview(self, doc: Document) -> dict:
        """Stands in for the real renderer (converts to PDF and thumbnails: slow, so cached)."""
        words = doc.content.split()
        return {"title": doc.title, "excerpt": " ".join(words[:40]), "words": len(words), "version": doc.version}

    def share(self, principal: Principal, doc_id: str, user_id: str, permission: str) -> None:
        doc = self._readable(principal, doc_id)
        if doc.owner_id != principal.user_id:
            raise Forbidden("only the owner can share")
        if permission not in ("view", "edit"):
            raise ValidationError("permission must be view or edit")
        self._docs.share(doc.id, user_id, permission)

    def create_link(self, principal: Principal, doc_id: str, hours: int) -> dict:
        doc = self._readable(principal, doc_id)
        if doc.owner_id != principal.user_id:
            raise Forbidden("only the owner can create links")
        if not 1 <= hours <= MAX_LINK_HOURS:
            raise ValidationError(f"links last 1 to {MAX_LINK_HOURS} hours")
        token = "lnk_" + secrets.token_urlsafe(24)
        expires = iso(self._clock.now() + timedelta(hours=hours))
        self._links.add(_hash(token), doc.id, principal.user_id, expires)
        return {"token": token, "expires_at": expires}

    def revoke_links(self, principal: Principal, doc_id: str) -> int:
        doc = self._readable(principal, doc_id)
        if doc.owner_id != principal.user_id:
            raise Forbidden("only the owner can revoke links")
        return self._links.revoke_for_doc(doc.id, iso(self._clock.now()))

    def open_link(self, token: str) -> Document:
        link = self._links.get(_hash(token))
        if link is None or link["revoked_at"] is not None:
            raise NotFound("this link doesn't exist or has been turned off")
        self._logger.info("link_opened", doc_id=link["doc_id"])
        return self._docs.get(link["doc_id"])
