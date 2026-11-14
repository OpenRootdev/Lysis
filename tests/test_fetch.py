import httpx

from lysis.ingestion.fetch import discover
from lysis.ingestion.github_client import GitHubClient


def test_discover_one_query_per_band(tmp_path):
    def handler(request):
        return httpx.Response(200, json={"items": [{"full_name": "a/b"}]})

    http = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com")
    gh = GitHubClient(token="x", cache_dir=tmp_path, client=http)
    assert discover(gh) == ["a/b"] * 3
    
def test_discover_uses_language(tmp_path):
    seen = []

    def handler(request):
        seen.append(request.url.params["q"])
        return httpx.Response(200, json={"items": []})

    http = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com")
    gh = GitHubClient(token="x", cache_dir=tmp_path, client=http)
    discover(gh, language="javascript")
    assert len(seen) == 3 and all('language:"javascript"' in q for q in seen)