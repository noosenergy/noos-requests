import pytest

from noos_pyk.clients import json


class TestDeserializeResponse:
    def test_no_json_content_raises_error(self, mocker):
        mocked_response = mocker.Mock()
        mocked_response.headers = {}
        mocked_response.status_code = 200

        with pytest.raises(json.JSONError):
            json._deserialize_response(mocked_response, "application/test-media-type")

    def test_response_without_json_content(self, mocker):
        mocked_response = mocker.Mock()
        mocked_response.headers = {}
        mocked_response.status_code = 204

        assert json._deserialize_response(mocked_response, "application/test-media-type") == {}

    def test_response_with_json_content(self, mocker):
        content_type = "application/test-media-type"
        mocked_response = mocker.Mock()
        mocked_response.headers = {"content-type": content_type}
        mocked_response.status_code = 200

        json._deserialize_response(mocked_response, content_type)

        mocked_response.json.assert_called_once()
