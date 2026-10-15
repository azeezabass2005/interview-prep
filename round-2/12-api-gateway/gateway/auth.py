from typing import Optional, Tuple

from .repositories.keys import ApiKeyRepository


class Authenticator:
    def __init__(self, keys: ApiKeyRepository):
        self._keys = keys

    def identify(self, api_key: Optional[str]) -> Optional[Tuple[str, str]]:
        if not api_key:
            return None
        return self._keys.lookup(api_key)
