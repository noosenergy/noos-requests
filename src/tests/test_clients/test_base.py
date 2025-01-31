import pytest

from noos_pyk.clients import base


@pytest.fixture
def bad_http_client() -> type[base.BaseHTTPClient]:
    class BadHTTPClient(base.BaseHTTPClient[str]):
        pass

    return BadHTTPClient


@pytest.fixture
def bad_ws_client() -> type[base.BaseWebSocketClient]:
    class BadWebSocketClient(base.BaseWebSocketClient[bytes]):
        pass

    return BadWebSocketClient


class TestNotImplementedClientMethod:
    def test_http_client_raises_error(self, bad_http_client):
        with pytest.raises(TypeError):
            bad_http_client()

    def test_ws_client_raises_error(self, bad_ws_client):
        with pytest.raises(TypeError):
            bad_ws_client()
