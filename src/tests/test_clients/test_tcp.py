import pytest
import websocket

from noos_pyk.clients import tcp


class TestWebSocketContext:
    def test_connect_then_close(self, mocker):
        mocked_connect = mocker.patch.object(websocket.WebSocket, "connect")
        mocked_close = mocker.patch.object(websocket.WebSocket, "close")
        url = "ws://test_url"
        ws = tcp.WebSocketContext()

        with ws.connect(url):
            pass

        mocked_connect.assert_called_once_with(url)
        mocked_close.assert_called_once()


class TestTCPClient:
    def test_initiate_connection(self):
        client = tcp.TCPClient("ws://test_url")

        assert client._conn is None
        assert isinstance(client.conn, tcp.WebSocketContext)
        assert client._conn is not None


class TestCheckResponse:
    def test_bad_request_raises_error(self, mocker):
        response = (8, mocker.Mock())

        with pytest.raises(tcp.TCPError):
            tcp._check_response(response)

    def test_mismatched_code_raises_error(self, mocker):
        response = (1, mocker.Mock())

        with pytest.raises(tcp.TCPError):
            tcp._check_response(response, statuses=(2,))


class TestPrepareUrl:
    @pytest.mark.parametrize(
        "base_url,path,params,final_url",
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
    def test_combine_url_compoments(self, base_url, path, params, final_url):
        assert tcp._prepare_url(base_url, path, params) == final_url
