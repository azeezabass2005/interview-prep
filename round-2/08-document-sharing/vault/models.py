from dataclasses import dataclass


@dataclass
class Document:
    id: str
    workspace_id: str
    owner_id: str
    title: str
    content: str
    version: int
    created_at: str
    updated_at: str
