import httpx

from lysis.ingestion.fetch import discover
from lysis.ingestion.github_client import GitHubClient


def test_discover_one_query_per_band(tmp_path):
    def handler(request):
        return httpx.Response(200, json={"items": [{"full_name": "a/b"}]})

    http = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com")
    gh = GitHubClient(token="x", cache_dir=tmp_path, client=http)
    assert discover(gh) == ["a/b"] * 3