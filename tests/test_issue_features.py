import pandas as pd

from lysis.features.issue_features import FEATURE_COLUMNS, build_features


def test_build_features():
    df = pd.DataFrame({"labels": [["good first issue", "bug"], []], "body_len": [100, 0]})
    f = build_features(df)
    assert list(f.columns) == FEATURE_COLUMNS
    assert f.loc[0, "gfi"] == 1 and f.loc[0, "bug"] == 1 and f.loc[0, "n_labels"] == 2
    assert f.loc[1].sum() == 0