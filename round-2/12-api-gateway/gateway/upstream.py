class FakeUpstream:
    def __init__(self):
        self.calls = 0

    def forward(self, path: str) -> dict:
        self.calls += 1
        return {"path": path, "data": "ok"}
