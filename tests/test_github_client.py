import httpx

from lysis.ingestion.github_client import GitHubClient


def make_client(handler, tmp_path):
    http = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.github.com")
    return GitHubClient(token="x", cache_dir=tmp_path, client=http)


def test_etag_cache_serves_304(tmp_path):
    seen = []

    def handler(request):
        etag = request.headers.get("If-None-Match")
        seen.append(etag)
        if etag == '"abc"':
            return httpx.Response(304)
        return httpx.Response(200, json=[{"number": 1}], headers={"ETag": '"abc"'})

    gh = make_client(handler, tmp_path)
    assert gh.get("/repos/o/r/issues") == [{"number": 1}]
    assert gh.get("/repos/o/r/issues") == [{"number": 1}]
    assert seen == [None, '"abc"']


def test_retries_after_rate_limit(tmp_path):
    responses = [
        httpx.Response(403, headers={"X-RateLimit-Remaining": "0", "Retry-After": "0"}),
        httpx.Response(200, json=[{"number": 2}]),
    ]
    gh = make_client(lambda request: responses.pop(0), tmp_path)
    assert gh.get("/x") == [{"number": 2}]


def test_list_issues_skips_prs(tmp_path):
    data = [{"number": 1}, {"number": 2, "pull_request": {}}]
    gh = make_client(lambda request: httpx.Response(200, json=data), tmp_path)
    assert gh.list_issues("o", "r") == [{"number": 1}]