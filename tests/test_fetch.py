import json

import httpx

from lysis.ingestion.fetch import discover, fetch_repo
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
    
def test_fetch_repo_catalog_only_skips_closed():
    calls = []

    class GH:
        def get(self, path, params=None):
            return []

        def list_issues(self, owner, repo, state="open"):
            calls.append(state)
            return []

    out = fetch_repo(GH(), "a/b", catalog_only=True)
    assert calls == ["open"] and out["closed_issues"] == []
    
def test_backfill_closed(tmp_path, monkeypatch):
    from lysis.ingestion import fetch as f

    monkeypatch.setattr(f, "OUT", tmp_path)
    for n, lang in (("a__x", "TypeScript"), ("b__y", "Go")):
        data = {
            "repo": {"full_name": n.replace("__", "/"), "language": lang},
            "closed_issues": [],
            "open_issues": [],
            "merged_prs": [],
        }
        (tmp_path / f"{n}.json").write_text(json.dumps(data))

    class GH:
        def list_issues(self, owner, repo, state="open"):
            return [{"number": 1}]

    f.backfill_closed(GH(), "typescript", None)
    assert json.loads((tmp_path / "a__x.json").read_text())["closed_issues"] == [{"number": 1}]
    assert json.loads((tmp_path / "b__y.json").read_text())["closed_issues"] == []