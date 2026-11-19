import pandas as pd

from lysis.models.transfer_eval import transfer


def test_transfer_runs(issues_df):
    big = pd.concat([issues_df] * 10, ignore_index=True)
    big["language"] = ["python", "python", "javascript", "javascript"] * (len(big) // 4)
    r = transfer(big, "python", "javascript")
    assert r["n_test"] == 100
    assert 0 <= r["transfer"]["auc"] <= 1