from lysis.features.rows import merged_times, pr_activity


def test_pr_activity_uses_only_past_prs():
    merged = merged_times(
        [
            {"merged_at": "2026-01-01T00:00:00Z"},
            {"merged_at": "2026-03-01T00:00:00Z"},
            {"merged_at": None},
        ]
    )
    out = pr_activity(merged, "2026-02-01T00:00:00Z")
    assert out == {"prs_90d": 1, "merge_gap_days": 31}