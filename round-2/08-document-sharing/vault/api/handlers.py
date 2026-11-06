from ..errors import ValidationError
from ..http import Request, Response
from ..models import Document


def doc_json(d: Document, content: bool = True) -> dict:
    body = {"id": d.id, "title": d.title, "owner_id": d.owner_id, "version": d.version, "updated_at": d.updated_at}
    if content:
        body["content"] = d.content
    return body


class Handlers:
    def __init__(self, docs):
        self._docs = docs

    def register(self, router) -> None:
        router.get("/health", lambda r: Response(200, {"status": "ok"}))
        router.get("/documents", self.list)
        router.post("/documents", self.create)
        router.get("/documents/{doc_id}", self.get)
        router.patch("/documents/{doc_id}", self.update)
        router.get("/documents/{doc_id}/preview", self.preview)
        router.post("/documents/{doc_id}/shares", self.share)
        router.post("/documents/{doc_id}/links", self.create_link)
        router.delete("/documents/{doc_id}/links", self.revoke_links)
        router.get("/search", self.search)
        router.get("/s/{token}", self.open_link)

    def list(self, request: Request) -> Response:
        docs, cursor = self._docs.page(request.principal, request.query.get("cursor"))
        return Response(200, {"documents": [doc_json(d, content=False) for d in docs], "next_cursor": cursor})

    def create(self, request: Request) -> Response:
        data = request.json()
        doc = self._docs.create(request.principal, str(data.get("title", "")), str(data.get("content", "")))
        return Response(201, doc_json(doc))

    def get(self, request: Request) -> Response:
        return Response(200, doc_json(self._docs.get(request.principal, request.params["doc_id"])))

    def update(self, request: Request) -> Response:
        data = request.json()
        try:
            version = int(data["version"])
        except (KeyError, TypeError, ValueError) as e:
            raise ValidationError("version is required") from e
        doc = self._docs.update(request.principal, request.params["doc_id"], str(data.get("content", "")), version)
        return Response(200, doc_json(doc))

    def preview(self, request: Request) -> Response:
        return Response(200, self._docs.preview(request.principal, request.params["doc_id"]))

    def share(self, request: Request) -> Response:
        data = request.json()
        self._docs.share(request.principal, request.params["doc_id"], str(data.get("user_id", "")),
                         str(data.get("permission", "view")))
        return Response(204)

    def create_link(self, request: Request) -> Response:
        hours = int(request.json().get("hours", 24))
        return Response(201, self._docs.create_link(request.principal, request.params["doc_id"], hours))

    def revoke_links(self, request: Request) -> Response:
        return Response(200, {"revoked": self._docs.revoke_links(request.principal, request.params["doc_id"])})

    def search(self, request: Request) -> Response:
        docs = self._docs.search(request.principal, request.query.get("q", ""))
        return Response(200, {"documents": [doc_json(d, content=False) for d in docs]})

    def open_link(self, request: Request) -> Response:
        return Response(200, doc_json(self._docs.open_link(request.params["token"])))
