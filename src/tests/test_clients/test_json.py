import pytest

from noos_pyk.clients import json


@pytest.fixture
def content_type() -> str:
    return "application/test-media-type"


class TestDeserializeResponse:
    def test_no_json_content_raises_error(self, content_type, mocker):
        mocked_response = mocker.Mock()
        mocked_response.headers = {}
        mocked_response.status_code = 200

        with pytest.raises(json.JSONError):
            json._deserialize_json_response(mocked_response, valid_content_type=content_type)

    def test_response_without_json_content(self, content_type, mocker):
        mocked_response = mocker.Mock()
        mocked_response.headers = {}
        mocked_response.status_code = 204

        assert (
            json._deserialize_json_response(mocked_response, valid_content_type=content_type) == {}
        )

    def test_response_with_json_content(self, content_type, mocker):
        mocked_response = mocker.Mock()
        mocked_response.headers = {"content-type": content_type}
        mocked_response.status_code = 200

        json._deserialize_json_response(mocked_response, valid_content_type=content_type)

        mocked_response.json.assert_called_once()
