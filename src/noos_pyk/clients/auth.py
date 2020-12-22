from typing import Optional, Type

from requests import auth
from typing_extensions import Protocol


class HTTPTokenAuth(auth.AuthBase):
    """Attaches a bearer token authentication header."""

    # Default token header and value
    default_header = "X-TokenAuth"
    default_value = "Token"

    def __init__(
        self, token: str, header: Optional[str] = None, value: Optional[str] = None
    ) -> None:
        self._token = token
        self._header = header or self.default_header
        self._value = value or self.default_value

    def __call__(self, r):
        r.headers[self._header] = f"{self._value} {self._token}"
        return r


class AuthClient(Protocol):
    """Mixin for authenticated clients (for token- or basic-based auth)."""

    _auth: Optional[auth.AuthBase] = None

    # Default token authentication class
    default_auth_class: Type[auth.AuthBase] = auth.HTTPBasicAuth

    def set_auth_header(self, *args) -> None:
        """Set authentication header."""
        self._auth = self.default_auth_class(*args)
