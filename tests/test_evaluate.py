import pandas as pd

from lysis.models.evaluate import precision_at_k, split_by_repo


def test_precision_at_k():
    assert precision_at_k([1, 0, 1, 0], [0.9, 0.8, 0.7, 0.1], 2) == 0.5


def test_split_has_no_shared_repos():
    df = pd.DataFrame({"repo": list("aabbccdd") * 3, "first_timer": [0, 1] * 12})
    train, test = split_by_repo(df, test_frac=0.5)
    assert set(train["repo"]).isdisjoint(set(test["repo"]))