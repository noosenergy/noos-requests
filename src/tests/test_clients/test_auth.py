from unittest import mock

import pytest
import requests

from noos_pyk.clients import auth, json


@pytest.fixture
def auth_class() -> type[auth.HTTPTokenAuth]:
    class TokenAuth(auth.HTTPTokenAuth):
        default_header = "Test-Header"
        default_value = "testKey"

    return TokenAuth


@pytest.fixture
def auth_client(auth_class) -> type[auth.AuthClient]:
    class AuthClient(json.JSONClient, auth.AuthClient):
        default_auth_class = auth_class

    return AuthClient


@pytest.fixture
def mocked_request(mocker, auth_client) -> mock.Mock:
    mocker.patch.object(auth_client, "_check")
    mocker.patch.object(auth_client, "_deserialize")
    return mocker.patch.object(requests.Session, "send")


def test_bearer_token_auth_header_correctly_formed(auth_client, mocked_request):
    client = auth_client(base_url="http://hostname/")
    client.set_auth_header("test_token")

    client.get("v1/test-endpoint")

    mocked_request.assert_called_once()

    args, _ = mocked_request.call_args

    assert "Test-Header" in args[0].headers
    assert args[0].headers["Test-Header"] == "testKey test_token"
