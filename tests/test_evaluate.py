import pandas as pd

from lysis.models.evaluate import evaluate, precision_at_k, split_by_repo


def test_precision_at_k():
    assert precision_at_k([1, 0, 1, 0], [0.9, 0.8, 0.7, 0.1], 2) == 0.5


def test_split_has_no_shared_repos():
    df = pd.DataFrame({"repo": list("aabbccdd") * 3, "first_timer": [0, 1] * 12})
    train, test = split_by_repo(df, test_frac=0.5)
    assert set(train["repo"]).isdisjoint(set(test["repo"]))
    
def test_evaluate_metrics():
    df = pd.DataFrame({"first_timer": [1, 0, 1, 0], "s": [0.9, 0.1, 0.8, 0.2]})
    r = evaluate(lambda d: d["s"], df, ks=(2,))
    assert r["auc"] == 1.0 and r["p@2"] == 1.0