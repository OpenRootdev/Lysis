import pandas as pd

from lysis.models.baseline import labels_only_ranker, rank_issues

DF = pd.DataFrame(
    {
        "labels": [["bug"], ["good first issue"], ["good first issue"]],
        "created_at": ["2026-11-01T00:00:00Z", "2024-01-01T00:00:00Z", "2026-11-01T00:00:00Z"],
    }
)


def test_labeled_and_fresh_ranks_first():
    s = labels_only_ranker(DF, now="2026-11-11T00:00:00Z")
    assert s[2] > s[1] > s[0]


def test_rank_issues_sorted_desc():
    r = rank_issues(DF, now="2026-11-11T00:00:00Z")
    assert r["score"].is_monotonic_decreasing
    assert r.loc[0, "created_at"] == "2026-11-01T00:00:00Z"
    assert r.loc[0, "labels"] == ["good first issue"]