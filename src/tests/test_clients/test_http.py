import random

import pytest
import requests

from noos_pyk.clients import http


@pytest.fixture
def bad_client():
    class BadClient(http.HTTPClient[str]):
        pass

    return BadClient


@pytest.fixture
def text_client():
    class TextClient(http.HTTPClient[str]):
        def _deserialize(self, response: requests.Response) -> str:
            return response.text

    return TextClient


@pytest.fixture
def mocked_request(mocker, text_client):
    mocker.patch.object(text_client, "_check")
    mocker.patch.object(text_client, "_deserialize")
    return mocker.patch.object(text_client, "_send")


@pytest.fixture
def error_status_code():
    return random.randrange(400, 600)


class TestHTTPClient:
    def test_not_implemented_deserialize_method_raises_error(self, bad_client):
        with pytest.raises(TypeError):
            bad_client()

    def test_client_initiates_connection_correctly(self, text_client):
        client = text_client(base_url="http://hostname/")

        assert client._conn is None
        assert isinstance(client.conn, requests.Session)
        assert client._conn is not None

    @pytest.mark.parametrize(
        "url,endpoint",
        [
            ("http://hostname/", "v1/test-endpoint"),
            ("http://hostname", "v1/test-endpoint"),
            ("http://hostname", "/v1/test-endpoint"),
            ("http://hostname/", "/v1/test-endpoint"),
        ],
    )
    def test_prepare_request_successfully(self, url, endpoint, text_client, mocked_request):
        client = text_client(base_url=url)

        client.get(endpoint)

        mocked_request.assert_called_once()

        args, kwargs = mocked_request.call_args

        assert args[0] == "GET"
        assert args[1] == "http://hostname/v1/test-endpoint"
        assert kwargs["data"] is None
        assert kwargs["params"] is None


class TestCheckResponse:
    def test_invalid_request_raises_error(self, error_status_code, mocker):
        response = requests.Response()
        mocker.patch.object(response, "status_code", error_status_code)

        with pytest.raises(http.HTTPError):
            http._check_response_status(response)

    def test_mismatched_response_status_code_raises_error(self, mocker):
        response = requests.Response()
        mocker.patch.object(response, "status_code", 201)

        with pytest.raises(http.HTTPError):
            http._check_response_status(response, statuses=(200,))
