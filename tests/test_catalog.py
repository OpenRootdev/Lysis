import numpy as np
import pandas as pd

from lysis.catalog import assign_levels, score_repo

AS_OF = pd.Timestamp("2026-11-01T00:00:00Z")


def raw(n_open=4):
    base = {
        "labels": [{"name": "good first issue"}],
        "comments": 0,
        "body": "x",
        "title": "t",
        "created_at": "2026-10-01T00:00:00Z",
        "html_url": "u",
        "assignees": [],
    }
    return {
        "repo": {
            "full_name": "a/b",
            "html_url": "https://github.com/a/b",
            "description": "d",
            "language": "Python",
            "stargazers_count": 10,
            "size": 500,
            "license": None,
            "created_at": "2020-01-01T00:00:00Z",
        },
        "open_issues": [{**base, "number": i} for i in range(n_open)],
        "merged_prs": [{"merged_at": "2026-10-20T00:00:00Z"}],
    }


def test_score_repo():
    e = score_repo(raw(), lambda df: np.full(len(df), 0.5), AS_OF)
    assert e["repo"] == "a/b" and e["language"] == "python"
    assert e["open_issues"] == 4 and e["good_first_issues"] == 4
    assert e["prs_90d"] == 1 and 0.4 < e["score"] <= 0.5
    assert e["validated"] is True


def test_too_few_open_issues_skipped():
    assert score_repo(raw(n_open=2), lambda df: np.zeros(len(df)), AS_OF) is None


def test_assign_levels():
    repos = [{"size_kb": s, "prs_90d": 5} for s in (10, 20, 30, 40, 50, 1000)]
    assign_levels(repos)
    assert repos[0]["level"] == "beginner" and repos[-1]["level"] == "advanced"
    assert all(r["active"] for r in repos)