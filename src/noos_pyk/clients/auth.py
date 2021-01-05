from typing import Optional, Protocol, Type

from requests import PreparedRequest, auth


DEFAULT_TOKEN_HEADER = "X-TokenAuth"
DEFAULT_TOKEN_VALUE = "Token"


class HTTPTokenAuth(auth.AuthBase):
    """Attaches a bearer token authentication header."""

    # Default token header and value
    default_header = DEFAULT_TOKEN_HEADER
    default_value = DEFAULT_TOKEN_VALUE

    def __init__(
        self, token: str, header: Optional[str] = None, value: Optional[str] = None
    ) -> None:
        self._token = token
        self._header = header or self.default_header
        self._value = value or self.default_value

    def __call__(self, request: PreparedRequest) -> PreparedRequest:
        request.headers[self._header] = f"{self._value} {self._token}"
        return request


class AuthClient(Protocol):
    """Mixin for authenticated clients (for token- or basic-based auth)."""

    _auth: Optional[auth.AuthBase] = None

    # Default token authentication class
    default_auth_class: Type[auth.AuthBase] = auth.HTTPBasicAuth

    def set_auth_header(self, *args) -> None:
        """Set authentication header."""
        self._auth = self.default_auth_class(*args)
