import pytest

from noos_pyk.clients import base


@pytest.fixture
def bad_client():
    class BadClient(base.BaseClient[str]):
        pass

    return BadClient


def test_not_implemented_request_method_raises_error(bad_client):
    with pytest.raises(TypeError):
        bad_client()
