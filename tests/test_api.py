import pytest
from fastapi.testclient import TestClient

from lysis.api import app, get_gh, get_model


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