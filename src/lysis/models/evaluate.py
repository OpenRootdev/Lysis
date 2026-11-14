"""Evaluate rankers by precision@k on first-timer labels, split by repo."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import GroupKFold

from lysis.features.rows import issue_row, merged_times
from lysis.models.baseline import labels_only_ranker
from lysis.models.gbm import make_gbm_ranker


def load_dataset(raw_dir="data/raw", labels_path="data/labels.csv"):
    labels = (
        pd.read_csv(labels_path)
        .groupby(["repo", "issue_number"], as_index=False)["first_timer"]
        .max()
    )
    rows = []
    for path in Path(raw_dir).glob("*.json"):
        d = json.loads(path.read_text())
        r = d["repo"]
        prs = d["merged_prs"]
        merged = merged_times(prs)
        starts = [pd.Timestamp(p["created_at"]) for p in prs]
        cutoff = min(starts) if starts else None
        rows += [
            issue_row(i, r, merged)
            for i in d["closed_issues"]
            if cutoff is not None and pd.Timestamp(i["created_at"]) >= cutoff
        ]
    df = pd.DataFrame(rows).merge(labels, on=["repo", "issue_number"], how="left")
    df["first_timer"] = df["first_timer"].fillna(0).astype(int)
    return df

def split_by_repo(df, test_frac=0.3, seed=42):
    repos = pd.Series(sorted(df["repo"].unique())).sample(frac=1, random_state=seed)
    test_repos = set(repos[: max(1, int(len(repos) * test_frac))])
    is_test = df["repo"].isin(test_repos)
    return df[~is_test], df[is_test]


def precision_at_k(y_true, scores, k):
    order = sorted(range(len(scores)), key=lambda i: -scores[i])[:k]
    return sum(y_true[i] for i in order) / len(order)


def evaluate(ranker, df, ks=(10, 50, 100)):
    """ranker: function(DataFrame) -> list of scores, higher = more beginner-friendly."""
    df = df.sample(frac=1, random_state=0).reset_index(drop=True)  # random tie-breaks
    y = df["first_timer"].tolist()
    scores = list(ranker(df))
    out = {f"p@{k}": round(precision_at_k(y, scores, k), 3) for k in ks if k <= len(y)}
    out["ap"] = round(average_precision_score(y, scores), 3)
    out["auc"] = round(roc_auc_score(y, scores), 3)
    return out


def random_ranker(df):
    return np.random.default_rng(0).random(len(df))

def cross_validate(df, rankers, n_splits=5):
    """rankers: {name: factory(train) -> ranker}. Mean AP/AUC over repo-grouped folds."""
    res = {n: {"ap": [], "auc": []} for n in rankers}
    for tr, te in GroupKFold(n_splits=n_splits).split(df, groups=df["repo"]):
        train, test = df.iloc[tr], df.iloc[te]
        for name, make in rankers.items():
            m = evaluate(make(train), test, ks=())
            res[name]["ap"].append(m["ap"])
            res[name]["auc"].append(m["auc"])
    return {n: {k: round(float(np.mean(v)), 3) for k, v in d.items()} for n, d in res.items()}


def main():
    df = load_dataset()
    train, test = split_by_repo(df)
    print(f"test: {len(test)} issues, {test['repo'].nunique()} repos")
    print(f"base rate: {test['first_timer'].mean():.3f}")
    print("random ranker:", evaluate(random_ranker, test))
    print("labels-only:", evaluate(labels_only_ranker, test))
    print("gbm:", evaluate(make_gbm_ranker(train), test))
    rankers = {
        "labels-only": lambda _: labels_only_ranker,
        "gbm": make_gbm_ranker,
    }
    print("cv:", cross_validate(df, rankers))


if __name__ == "__main__":
    main()