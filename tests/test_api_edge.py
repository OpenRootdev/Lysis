import pytest
from fastapi.testclient import TestClient

from lysis import api as api_module
from lysis.api import app, get_catalog, get_model
from lysis.limits import SlidingWindow, TTLCache


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(api_module, "PER_IP", SlidingWindow(1000))
    monkeypatch.setattr(api_module, "GLOBAL", SlidingWindow(1000))
    monkeypatch.setattr(api_module, "FEEDBACK", SlidingWindow(1000))
    monkeypatch.setattr(api_module, "REPOS", SlidingWindow(1000))
    monkeypatch.setattr(api_module, "CACHE", TTLCache(ttl=600))
    monkeypatch.setattr(api_module, "log_feedback", lambda *a, **k: True)
    app.dependency_overrides[get_model] = lambda: (None, {"trained_at": "2026-01-01T00:00:00"})
    app.dependency_overrides[get_catalog] = lambda: {
        "meta": {"model_date": "2026-01-01"},
        "repos": [],
    }
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.mark.parametrize(
    "repo",
    ["", "noslash", "a/b/c", "a b/c", "../etc/passwd", "a/b;drop", "a/" + "b" * 5 + "<script>"],
)
def test_rank_rejects_bad_repo(client, repo):
    assert client.get("/rank", params={"repo": repo}).status_code == 422


@pytest.mark.parametrize("top", [0, 31, -1, "x"])
def test_rank_rejects_bad_top(client, top):
    assert client.get("/rank", params={"repo": "a/b", "top": top}).status_code == 422


@pytest.mark.parametrize("lang", ["Py thon", "UPPER", "a" * 31, "py;x"])
def test_repos_rejects_bad_language(client, lang):
    assert client.get("/repos", params={"language": lang}).status_code == 422


def test_repos_rejects_bad_level_and_top(client):
    assert client.get("/repos", params={"level": "expert"}).status_code == 422
    assert client.get("/repos", params={"top": 51}).status_code == 422


def test_rank_429_has_retry_after(client, monkeypatch):
    monkeypatch.setattr(api_module, "PER_IP", SlidingWindow(1))
    client.get("/rank", params={"repo": "bad"})
    r = client.get("/rank", params={"repo": "bad"})
    assert r.status_code == 429
    assert r.headers["retry-after"] == "60"


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"repo": "a/b", "issue_number": 0, "score": 0.5, "helpful": True, "model_date": "2026-01-01"},
        {"repo": "a/b", "issue_number": 1, "score": 1.5, "helpful": True, "model_date": "2026-01-01"},
        {"repo": "a/b", "issue_number": 1, "score": -0.1, "helpful": True, "model_date": "2026-01-01"},
        {"repo": "bad", "issue_number": 1, "score": 0.5, "helpful": True, "model_date": "2026-01-01"},
        {"repo": "a/b", "issue_number": 1, "score": 0.5, "helpful": True, "model_date": "01-01-2026"},
    ],
)
def test_feedback_rejects_invalid_body(client, body):
    assert client.post("/feedback", json=body).status_code == 422


def test_feedback_valid_returns_201(client):
    body = {"repo": "a/b", "issue_number": 1, "score": 0.5, "helpful": True, "model_date": "2026-01-01"}
    assert client.post("/feedback", json=body).status_code == 201


def test_feedback_429(client, monkeypatch):
    monkeypatch.setattr(api_module, "FEEDBACK", SlidingWindow(1))
    body = {"repo": "a/b", "issue_number": 1, "score": 0.5, "helpful": True, "model_date": "2026-01-01"}
    client.post("/feedback", json=body)
    assert client.post("/feedback", json=body).status_code == 429