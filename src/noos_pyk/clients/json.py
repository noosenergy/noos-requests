import cgi
from http import client as http_client
from typing import Any, Dict

import requests

from . import base, http


Json = Dict[str, Any]

DEFAULT_JSON_CONTENT_TYPE = "application/json"


class JSONError(base.ClientError):
    """Exception encountered retrieving JSON content."""

    pass


class JSONClient(http.HTTPClient[Json]):
    """Base class for JSON clients."""

    # Default JSON response back
    default_content_type = DEFAULT_JSON_CONTENT_TYPE

    def _deserialize(self, response: requests.Response) -> Json:
        return _deserialize_json_response(response, valid_content_type=self.default_content_type)


# Helpers:


def _deserialize_json_response(
    response: requests.Response, valid_content_type: str = DEFAULT_JSON_CONTENT_TYPE
) -> Json:
    content_type, _ = cgi.parse_header(response.headers.get("content-type", ""))

    if content_type == valid_content_type:
        return response.json()

    # When 204 is returned, there is explicitly no content.
    if response.status_code == http_client.NO_CONTENT:
        return {}

    raise JSONError(f"No JSON content returned: {response.text}")
