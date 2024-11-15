from contextlib import contextmanager
from typing import Optional, Tuple, TypeVar, Union
from urllib import parse

import websocket

from . import base


T = TypeVar("T")


class WebSocketError(base.ClientError):
    """Exception encountered over a web-socket client connection."""

    pass


class WebSocketContext(websocket.WebSocket):
    @contextmanager
    def connect(self, url, **options):
        """Start web-socket connection to URL."""
        super().connect(url, **options)
        yield
        self.close()


class WebSocketClient(base.BaseWebSocketClient[T]):
    """Base class for short-lived web-socket clients."""

    _conn: Optional[WebSocketContext] = None

    @property
    def conn(self) -> WebSocketContext:
        """Web-socket client connection object."""
        if self._conn is None:
            self._conn = WebSocketContext()
            self._conn.settimeout(self._timeout)
        return self._conn

    # Short-lived client implementation:

    def receive(self, path: str, params: Optional[dict] = None, opcode: int = 0) -> T:
        url = self._prepare(path, params=params)
        return self._recv(url, opcode=opcode)

    def send(
        self, path: str, data: Union[bytes, str], params: Optional[dict] = None, opcode: int = 0
    ) -> None:
        url = self._prepare(path, params=params)
        self._send(url, data=data, opcode=opcode)

    # Helpers:

    def _recv(self, url: str, opcode: int = 0) -> T:
        with self.conn.connect(url):
            response: Tuple[int, T] = self.conn.recv_data()
            _check_response_code(response[0], opcode=opcode)
        return response[1]

    def _send(self, url: str, data: Union[bytes, str], opcode: int = 0) -> None:
        with self.conn.connect(url):
            self.conn.send(data, opcode=opcode)

    def _prepare(self, path: str, params: Optional[dict] = None) -> str:
        return _prepare_url(self._url, path, params)


# Helpers:


def _prepare_url(base_url: str, path: str, params: Optional[dict]) -> str:
    url = parse.urljoin(base_url, path)
    parsed_url = parse.urlparse(url)
    return parse.ParseResult(
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        parse.urlencode(params) if params else "",
        parsed_url.fragment,
    ).geturl()


def _check_response_code(response_code: int, opcode: int = 0) -> None:
    # Expected codes: (https://tools.ietf.org/html/rfc6455)
    if response_code == websocket.ABNF.OPCODE_CLOSE:
        raise WebSocketError("Invalid message code - connection closed")

    if response_code != opcode:
        raise WebSocketError(f"Invalid message code - expected {opcode}, got {response_code}")
