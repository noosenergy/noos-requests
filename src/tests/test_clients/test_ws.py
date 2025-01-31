from unittest import mock

import pytest
import websocket

from noos_pyk.clients import ws


@pytest.fixture
def text_client() -> type[ws.WebSocketClient]:
    class TextClient(ws.WebSocketClient[str]):
        pass

    return TextClient


@pytest.fixture
def mocked_message(mocker, text_client) -> mock.Mock:
    return mocker.patch.object(text_client, "_recv")


class TestWebSocketContext:
    def test_connect_then_close(self, mocker):
        mocked_connect = mocker.patch.object(websocket.WebSocket, "connect")
        mocked_close = mocker.patch.object(websocket.WebSocket, "close")
        url = "ws://test_url"
        conn = ws.WebSocketContext()

        with conn.connect(url):
            pass

        mocked_connect.assert_called_once_with(url)
        mocked_close.assert_called_once()


class TestWebSocketClient:
    def test_client_initiates_connection_correctly(self, text_client):
        client = text_client("ws://hostname/")

        assert client._conn is None
        assert isinstance(client.conn, ws.WebSocketContext)
        assert client._conn is not None

    def test_received_message_successfully(self, text_client, mocked_message):
        client = text_client(base_url="ws://hostname:8000/")

        client.receive(
            "/v1/ws", params={"filter": "test_value"}, opcode=websocket.ABNF.OPCODE_TEXT
        )

        mocked_message.assert_called_once()

        args, kwargs = mocked_message.call_args

        assert args[0] == "ws://hostname:8000/v1/ws?filter=test_value"
        assert kwargs["opcode"] == 1

    def test_sent_message_successfully(self, text_client, mocker):
        mocked_send = mocker.patch.object(text_client, "_send")
        client = text_client(base_url="ws://hostname:8000/")

        client.send(
            "/v1/ws",
            data="test_data",
            params={"filter": "test_value"},
            opcode=websocket.ABNF.OPCODE_TEXT,
        )

        mocked_send.assert_called_once()

        args, kwargs = mocked_send.call_args

        assert args[0] == "ws://hostname:8000/v1/ws?filter=test_value"
        assert kwargs["data"] == "test_data"
        assert kwargs["opcode"] == 1


class TestPrepareUrl:
    @pytest.mark.parametrize(
        "base_url,path,params,full_url",
        [
            # Test join
            ("ws://hostname:8000", "/ws", None, "ws://hostname:8000/ws"),
            ("ws://hostname:8000/v1", "/v1/ws", None, "ws://hostname:8000/v1/ws"),
            # Test add query
            (
                "ws://hostname:8000/v1",
                "/v1/ws",
                {"filter": "test_value"},
                "ws://hostname:8000/v1/ws?filter=test_value",
            ),
            # Test add safe query
            (
                "ws://hostname:8000/v1",
                "/v1/ws",
                {"filter": "2020-02-28T00:00:00"},
                "ws://hostname:8000/v1/ws?filter=2020-02-28T00%3A00%3A00",
            ),
        ],
    )
    def test_combine_url_compoments_successfully(self, base_url, path, params, full_url):
        assert ws._prepare_url(base_url, path, params) == full_url


class TestCheckResponseCode:
    def test_closed_code_raises_error(self, mocker):
        opcode = websocket.ABNF.OPCODE_CLOSE

        with pytest.raises(ws.WebSocketError):
            ws._check_response_code(opcode)

    def test_mismatched_code_raises_error(self, mocker):
        opcode = websocket.ABNF.OPCODE_TEXT

        with pytest.raises(ws.WebSocketError):
            ws._check_response_code(opcode, opcode=websocket.ABNF.OPCODE_BINARY)
