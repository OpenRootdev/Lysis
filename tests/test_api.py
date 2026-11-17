import pytest
from fastapi.testclient import TestClient

from lysis import api as api_module
from lysis.api import app, get_catalog, get_gh, get_model
from lysis.limits import SlidingWindow


class FakeGH:
    def get(self, path, params=None):
        if path.endswith("/pulls"):
            return []
        return {
            "full_name": "a/b",
            "license": None,
            "language": "Python",
            "created_at": "2020-01-01T00:00:00Z",
        }

    def list_issues(self, owner, repo, state="open"):
        base = {
            "labels": [],
            "comments": 0,
            "body": "x",
            "created_at": "2026-01-01T00:00:00Z",
            "html_url": "u",
            "assignees": [],
        }
        return [
            {**base, "number": 1, "title": "one"},
            {**base, "number": 2, "title": "two", "labels": [{"name": "good first issue"}]},
        ]
    
    api_module.PER_IP.hits.clear()
    api_module.GLOBAL.hits.clear()
    api_module.CACHE.data.clear()



@pytest.fixture
def api():
    app.dependency_overrides[get_gh] = lambda: FakeGH()
    app.dependency_overrides[get_model] = lambda: (
        lambda df: df["labels"].apply(len),
        {"trained_at": "2026-11-14T00:00:00+00:00"},
    )
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health(api):
    assert api.get("/health").json() == {"status": "ok"}


def test_rank(api):
    r = api.get("/rank", params={"repo": "a/b", "top": 5})
    assert r.status_code == 200
    body = r.json()
    assert [i["number"] for i in body["issues"]] == [2, 1]
    assert body["model_date"] == "2026-11-14"
    assert "body" not in body["issues"][0] and "why" not in body["issues"][0]


def test_rank_rejects_bad_repo(api):
    assert api.get("/rank", params={"repo": "nonsense"}).status_code == 422
    
    
def test_rank_is_cached(api):
    calls = []
    app.dependency_overrides[get_model] = lambda: (
        lambda df: calls.append(1) or df["labels"].apply(len),
        {"trained_at": "2026-11-14T00:00:00+00:00"},
    )
    for _ in range(2):
        assert api.get("/rank", params={"repo": "a/b"}).status_code == 200
    assert len(calls) == 1


def test_per_ip_limit(api, monkeypatch):
    monkeypatch.setattr(api_module, "PER_IP", SlidingWindow(2))
    codes = [api.get("/rank", params={"repo": "a/b"}).status_code for _ in range(3)]
    assert codes == [200, 200, 429]

def test_cors_allows_local_frontend(api):
    r = api.get("/health", headers={"Origin": "http://localhost:3000"})
    assert r.headers["access-control-allow-origin"] == "http://localhost:3000"
    
    
def vote_body(**kw):
    return {
        "repo": "a/b",
        "issue_number": 5,
        "score": 0.3,
        "helpful": True,
        "model_date": "2026-11-14",
        **kw,
    }


def test_feedback_saved(api, monkeypatch):
    seen = []
    monkeypatch.setattr(api_module, "log_feedback", lambda *a: seen.append(a) or True)
    r = api.post("/feedback", json=vote_body())
    assert r.status_code == 201
    assert seen == [("a/b", 5, 0.3, True, "2026-11-14")]


def test_feedback_rejects_bad_input(api):
    assert api.post("/feedback", json=vote_body(repo="nonsense")).status_code == 422
    assert api.post("/feedback", json=vote_body(score=5)).status_code == 422


def test_feedback_failure_is_502(api, monkeypatch):
    monkeypatch.setattr(api_module, "log_feedback", lambda *a: False)
    assert api.post("/feedback", json=vote_body()).status_code == 502


CATALOG = {
    "meta": {
        "built_at": "2026-11-17T00:00:00+00:00",
        "model_date": "2026-11-14",
        "n_repos": 4,
        "thresholds": {},
    },
    "repos": [
        {"repo": "a/one", "language": "python", "level": "beginner", "active": True},
        {"repo": "a/two", "language": "python", "level": "advanced", "active": True},
        {"repo": "a/three", "language": "javascript", "level": "beginner", "active": True},
        {"repo": "a/four", "language": "python", "level": "beginner", "active": False},
    ],
}


@pytest.fixture
def cat_api():
    api_module.REPOS.hits.clear()
    app.dependency_overrides[get_catalog] = lambda: CATALOG
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_repos_filters(cat_api):
    r = cat_api.get("/repos", params={"language": "python", "level": "beginner"}).json()
    assert [x["repo"] for x in r["repos"]] == ["a/one"]
    assert r["total"] == 1


def test_repos_include_inactive(cat_api):
    params = {"language": "python", "level": "beginner", "active_only": "false"}
    r = cat_api.get("/repos", params=params).json()
    assert [x["repo"] for x in r["repos"]] == ["a/one", "a/four"]


def test_repos_top_and_validation(cat_api):
    assert len(cat_api.get("/repos", params={"top": 1}).json()["repos"]) == 1
    assert cat_api.get("/repos", params={"level": "expert"}).status_code == 422


def test_repos_meta(cat_api):
    m = cat_api.get("/repos/meta").json()
    assert m["languages"] == ["javascript", "python"] and m["n_repos"] == 4