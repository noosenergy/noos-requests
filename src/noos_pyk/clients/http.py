import abc
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from urllib import parse

import niquests as requests
from niquests import auth

from . import base


T = TypeVar("T")


class HTTPError(base.ClientError):
    """Exception encountered over a HTTP client connection."""

    pass


class HTTPClient(base.BaseHTTPClient[T]):
    """Base class for blocking HTTP clients."""

    _auth: auth.AuthBase | None = None
    _conn: requests.Session | None = None

    @property
    def conn(self) -> requests.Session:
        """HTTP client connection object."""
        if self._conn is None:
            self._conn = requests.Session()
            # Niquests types header keys as str | bytes. Our headers are str-only.
            self._conn.headers.update(cast(Mapping[str | bytes, str | bytes], self._headers))
        return self._conn

    # Blocking client implementation:

    def _request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        data: dict | None = None,
        form_data: Any | None = None,
        statuses: tuple = (),
    ) -> T:
        url = parse.urljoin(self._url, path)
        response = self._send(method, url, params=params, data=data, form_data=form_data)

        self._check(response, statuses=statuses)
        return self._deserialize(response)

    # Helpers:

    def _send(
        self,
        method: str,
        url: str,
        params: dict | None = None,
        data: dict | None = None,
        form_data: Any | None = None,
    ) -> requests.Response:
        """Fetch request response."""
        return self.conn.request(
            method,
            url,
            params=params,
            json=data,
            data=form_data,
            headers=self._headers,
            timeout=self._timeout,
            auth=self._auth,
        )

    @staticmethod
    def _check(response: requests.Response, statuses: tuple = ()) -> None:
        """Check response status."""
        _check_response_status(response, statuses=statuses)

    @abc.abstractmethod
    def _deserialize(self, response: requests.Response) -> T:
        """Deserialize response content."""
        ...


# Helpers:


def _check_response_status(response: requests.Response, statuses: tuple = ()) -> None:
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        raise HTTPError(f"{response.status_code}: {response.text}")
    else:
        if response.status_code not in statuses:
            codes = ",".join([str(status) for status in statuses])
            raise HTTPError(f"Unexpected {response.status_code} response: expected {codes}")
