from dataclasses import dataclass, field

from ..errors import DocError
from ..services.editing import EditingService
from ..services.search import SearchService


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)


class DocsApi:
    def __init__(self, editing: EditingService, search: SearchService):
        self._editing = editing
        self._search = search

    def _run(self, fn):
        try:
            return fn()
        except DocError as e:
            return Response(e.status, {"error": str(e)})

    def post_document(self, user: str, body: dict) -> Response:
        return self._run(lambda: Response(201, {"doc_id": self._editing.create(user, body.get("title", ""),
                                                                               body.get("content", ""))}))

    def put_content(self, user: str, doc_id: int, body: dict) -> Response:
        return self._run(lambda: Response(200, {"version": self._editing.save(doc_id, user, body["content"],
                                                                              body["base_version"])}))

    def post_restore(self, user: str, doc_id: int, version: int) -> Response:
        return self._run(lambda: Response(200, {"version": self._editing.restore(doc_id, user, version)}))

    def get_document(self, doc_id: int) -> Response:
        def go():
            v = self._editing.latest(doc_id)
            return Response(200, {"doc_id": doc_id, "version": v.version, "content": v.content})
        return self._run(go)

    def get_history(self, doc_id: int) -> Response:
        return self._run(lambda: Response(200, {"versions": [v.version for v in self._editing.history(doc_id)]}))

    def get_search(self, q: str) -> Response:
        return Response(200, {"doc_ids": self._search.search(q)})
