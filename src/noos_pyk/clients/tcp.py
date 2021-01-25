from contextlib import contextmanager
from typing import Any, Optional, Tuple
from urllib import parse

import websocket

from . import base


class TCPError(base.ClientError):
    """Exception encountered over a TCP client connection."""

    pass


class WebSocketContext(websocket.WebSocket):
    @contextmanager
    def connect(self, url, **options):
        """Connect to URL.

        Websocket url scheme: `ws://host:port/resource`

        You can customize using 'options'.
        If you set "header" list object, you can set your own custom header.

        >>> ws = WebSocket()
        >>> ws.connect("ws://echo.websocket.org/",
                ...     header=["User-Agent: MyProgram",
                ...             "x-custom: header"])
        """
        super().connect(url, **options)
        yield
        self.close()


class TCPClient:
    """Base class for TCP clients."""

    _conn: Optional[WebSocketContext] = None

    # Default connection timeout at 20''
    default_timeout = 20

    def __init__(self, base_url: str, default_timeout: Optional[float] = None) -> None:
        self._url = base_url
        self._timeout = default_timeout or self.default_timeout

    @property
    def conn(self) -> WebSocketContext:
        """TCP client connection object."""
        if self._conn is None:
            self._conn = WebSocketContext()
            self._conn.settimeout(self._timeout)
        return self._conn

    # Public TCP methods:

    def _receive(self, path: str, params: Optional[dict] = None, statuses: tuple = ()) -> Any:
        url = _prepare_url(self._url, path, params)

        with self.conn.connect(url):
            response = self.conn.recv_data()
            _check_response(response, statuses=statuses)

        return response[1]


# Helpers:


def _prepare_url(base_url: str, path: str, params: Optional[dict]) -> str:
    full_url = parse.urljoin(base_url, path)
    parsed_url = parse.urlparse(full_url)
    return parse.ParseResult(
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        parse.urlencode(params) if params else "",
        parsed_url.fragment,
    ).geturl()


def _check_response(response: Tuple[int, Any], statuses: tuple = ()) -> None:
    # Expected codes: (https://tools.ietf.org/html/rfc6455)
    response_code = response[0]

    if response_code == 8:
        raise TCPError("Invalid message - connection closed")

    if response_code not in statuses:
        raise TCPError("Invalid message - unexpected data type")
