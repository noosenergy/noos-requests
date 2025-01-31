import abc
from typing import Any, TypeVar


T = TypeVar("T")

Header = dict[str, str]

DEFAULT_TIMEOUT = 10.0


class ClientError(Exception):
    """Basic exception raised by a client."""

    pass


class BaseHTTPClient[T](abc.ABC):
    """Interface class for HTTP clients."""

    _url: str
    _timeout: float
    _headers: Header

    # Default base URL
    default_base_url: str = ""

    # Default connection timeout
    default_timeout: float = DEFAULT_TIMEOUT

    # Default request media type
    default_content_type: str = ""

    def __init__(
        self,
        base_url: str | None = None,
        default_timeout: float | None = None,
        default_headers: Header | None = None,
    ) -> None:
        self._url = base_url or self.default_base_url
        self._timeout = default_timeout or self.default_timeout
        self._headers = default_headers or {"Accept": self.default_content_type}

    # Default HTTP methods:

    def get(self, path: str, params: dict | None = None, statuses: tuple = ()) -> T:
        return self._request(method="GET", path=path, params=params, statuses=statuses)

    def delete(self, path: str, params: dict | None = None, statuses: tuple = ()) -> T:
        return self._request(method="DELETE", path=path, params=params, statuses=statuses)

    def post(
        self,
        path: str,
        params: dict | None = None,
        data: dict | None = None,
        form_data: Any | None = None,
        statuses: tuple = (),
    ) -> T:
        return self._request(
            method="POST",
            path=path,
            params=params,
            data=data,
            form_data=form_data,
            statuses=statuses,
        )

    def put(
        self,
        path: str,
        data: dict | None = None,
        form_data: Any | None = None,
        statuses: tuple = (),
    ) -> T:
        return self._request(
            method="PUT",
            path=path,
            data=data,
            form_data=form_data,
            statuses=statuses,
        )

    def patch(
        self,
        path: str,
        data: dict | None = None,
        form_data: Any | None = None,
        statuses: tuple = (),
    ) -> T:
        return self._request(
            method="PATCH",
            path=path,
            data=data,
            form_data=form_data,
            statuses=statuses,
        )

    # Bespoke client implementation:

    @abc.abstractmethod
    def _request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        data: dict | None = None,
        form_data: Any | None = None,
        statuses: tuple = (),
    ) -> T: ...


class BaseWebSocketClient[T](abc.ABC):
    """Interface class for web-socket clients."""

    _url: str
    _timeout: float
    _headers: Header

    # Default base URL
    default_base_url: str = ""

    # Default socket timeout
    default_timeout: float = DEFAULT_TIMEOUT

    def __init__(
        self,
        base_url: str | None = None,
        default_headers: Header | None = None,
        default_timeout: float | None = None,
    ) -> None:
        self._url = base_url or self.default_base_url
        self._timeout = default_timeout or self.default_timeout
        self._headers = default_headers or {}

    # Default WebSocket methods:

    @abc.abstractmethod
    def send(
        self, path: str, data: bytes | str, params: dict | None = None, opcode: int = 0
    ) -> None: ...

    @abc.abstractmethod
    def receive(self, path: str, params: dict | None = None, opcode: int = 0) -> T: ...
