import abc
from typing import Optional, TypeVar
from urllib import parse

import requests
from requests import auth

from . import base


T = TypeVar("T")


class HTTPError(base.ClientError):
    """Exception encountered over a HTTP client connection."""

    pass


class HTTPClient(base.BaseClient[T]):
    """Base class for blocking HTTP clients."""

    _auth: Optional[auth.AuthBase] = None
    _conn: Optional[requests.Session] = None

    @property
    def conn(self) -> requests.Session:
        """HTTP client connection object."""
        if self._conn is None:
            self._conn = requests.Session()
            self._conn.headers.update(self._headers)
        return self._conn

    # Blocking client implementation:

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        statuses: tuple = (),
    ) -> T:
        url = parse.urljoin(self._url, path)
        response = self._send(method, url, params=params, data=data)

        self._check(response, statuses=statuses)
        return self._deserialize(response)

    # Helpers:

    def _send(
        self, method: str, url: str, params: Optional[dict] = None, data: Optional[dict] = None
    ) -> requests.Response:
        """Fetch request response."""
        return self.conn.request(
            method,
            url,
            params=params,
            json=data,
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
