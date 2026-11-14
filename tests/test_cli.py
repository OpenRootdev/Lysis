from lysis.cli import rank_repo


class FakeGH:
    def get(self, path, params=None):
        if path.endswith("/pulls"):
            return []
        return {"full_name": "a/b", "license": None, "created_at": "2020-01-01T00:00:00Z"}

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
            {**base, "number": 3, "title": "taken", "assignees": [{"login": "x"}]},
        ]


def test_rank_repo():
    out = rank_repo(FakeGH(), "a/b", lambda df: df["labels"].apply(len), top=5)
    assert list(out["number"]) == [2, 1]