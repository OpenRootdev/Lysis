from lysis.features.issue_features import FEATURE_COLUMNS, build_features


def test_build_features(issues_df):
    f = build_features(issues_df)
    assert list(f.columns) == FEATURE_COLUMNS
    assert f.loc[0, "gfi"] == 1 and f.loc[0, "is_maintainer"] == 0
    assert f.loc[1, "is_maintainer"] == 1 and f.loc[1, "has_code"] == 1
    assert f.notna().all().all()