"""Evaluate rankers by precision@k on first-timer labels, split by repo."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

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
        name = r["full_name"]
        rows += [
        {
                "repo": name,
                "issue_number": i["number"],
                "labels": [x["name"].lower() for x in i["labels"]],
                "comments": i["comments"],
                "body_len": len(i.get("body") or ""),
                "title_len": len(i.get("title") or ""),
                "has_code": int("```" in (i.get("body") or "")),
                "author_assoc": i.get("author_association") or "NONE",
                "stars": r["stargazers_count"],
                "forks": r["forks_count"],
                "repo_size": r["size"],
                "has_license": int(bool(r.get("license"))),
                "repo_created_at": r["created_at"],
                "created_at": i["created_at"],
            }
            for i in d["closed_issues"]
        ]
    return labels.merge(pd.DataFrame(rows), on=["repo", "issue_number"])


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
    return {f"p@{k}": round(precision_at_k(y, scores, k), 3) for k in ks if k <= len(y)}


def random_ranker(df):
    return np.random.default_rng(0).random(len(df))


def main():
    df = load_dataset()
    train, test = split_by_repo(df)
    print(f"test: {len(test)} issues, {test['repo'].nunique()} repos")
    print(f"base rate: {test['first_timer'].mean():.3f}")
    print("random ranker:", evaluate(random_ranker, test))
    print("labels-only:", evaluate(labels_only_ranker, test))
    print("gbm:", evaluate(make_gbm_ranker(train), test))


if __name__ == "__main__":
    main()