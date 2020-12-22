import cgi
from http import client as http_client
from typing import Any, Dict

import requests

from . import base, http


Json = Dict[str, Any]


class JSONError(base.ClientError):
    """Exception encountered retrieving JSON content."""

    pass


class JSONClient(http.HTTPClient[Json]):
    """Base class for JSON clients."""

    # Default JSON response back
    default_content_type = "application/json"

    def _deserialize(self, response: requests.Response) -> Json:
        return _deserialize_response(response, self.default_content_type)


# Helpers:


def _deserialize_response(response: requests.Response, valid_content_type: str) -> Json:
    content_type, _ = cgi.parse_header(response.headers.get("content-type", ""))
    if content_type == valid_content_type:
        return response.json()

    # When 204 is returned, there is explicitly no content.
    if response.status_code == http_client.NO_CONTENT:
        return {}

    raise JSONError(f"No JSON content returned: {response.text}")
