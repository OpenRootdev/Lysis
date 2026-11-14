import pandas as pd
import pytest


@pytest.fixture
def issues_df():
    return pd.DataFrame(
        {
            "labels": [["good first issue"], [], ["good first issue", "bug"], ["bug"]] * 5,
            "body_len": [50, 10, 80, 200] * 5,
            "title_len": [30, 20, 40, 60] * 5,
            "has_code": [0, 1, 0, 1] * 5,
            "author_assoc": ["NONE", "MEMBER", "NONE", "OWNER"] * 5,
            "prs_90d": [5, 20, 5, 10] * 5,
            "merge_gap_days": [2, 1, 2, 30] * 5,
            "has_license": [1, 1, 0, 1] * 5,
            "created_at": ["2026-01-10T00:00:00Z"] * 20,
            "repo_created_at": ["2020-01-01T00:00:00Z"] * 20,
            "first_timer": [1, 0, 1, 0] * 5,
            
        }
    )