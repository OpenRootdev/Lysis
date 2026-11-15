import httpx
import pytest

from lysis.client import ApiError, fetch_rank


def client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_fetch_rank_params():
    seen = {}

    def handler(request):
        seen["q"] = dict(request.url.params)
        return httpx.Response(200, json={"issues": []})

    out = fetch_rank("https://x.test/", "a/b", 5, http=client(handler))
    assert out == {"issues": []}
    assert seen["q"] == {"repo": "a/b", "top": "5", "explain": "true"}


def test_api_error_includes_detail():
    http = client(lambda r: httpx.Response(404, json={"detail": "GitHub error 404"}))
    with pytest.raises(ApiError, match="404"):
        fetch_rank("https://x.test", "a/b", 5, http=http)


def test_api_unreachable():
    def handler(request):
        raise httpx.ConnectError("down")

    with pytest.raises(ApiError, match="unreachable"):
        fetch_rank("https://x.test", "a/b", 5, http=client(handler))