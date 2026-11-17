"""Does aggregating issue scores to repo level predict repo-level first-timer success?"""

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold

from lysis.models.evaluate import load_dataset
from lysis.models.gbm import make_gbm_ranker


def oof_scores(df, make, n_splits=5):
    df = df.reset_index(drop=True)
    out = np.zeros(len(df))
    for tr, te in GroupKFold(n_splits=n_splits).split(df, groups=df["repo"]):
        out[te] = list(make(df.iloc[tr])(df.iloc[te]))
    return out


def repo_table(df, scores, min_issues=30, top=5):
    d = df.assign(score=scores)
    d["gfi"] = d["labels"].apply(lambda ls: int("good first issue" in ls))
    rows = []
    for repo, g in d.groupby("repo"):
        if len(g) < min_issues:
            continue
        rows.append(
            {
                "repo": repo,
                "language": g["language"].iloc[0],
                "n": len(g),
                "truth": g["first_timer"].mean(),
                "mean_all": g["score"].mean(),
                "top5_mean": g["score"].nlargest(top).mean(),
                "gfi_share": g["gfi"].mean(),
            }
        )
    return pd.DataFrame(rows)


def evaluate_repos(t, k=20):
    res = {}
    for c in ["mean_all", "top5_mean", "gfi_share"]:
        res[c] = {
            "spearman": round(t[c].corr(t["truth"], method="spearman"), 3),
            f"truth@{k}": round(t.nlargest(k, c)["truth"].mean(), 3),
        }
    return t["truth"].mean(), res


def main():
    df = load_dataset()
    t = repo_table(df, oof_scores(df, make_gbm_ranker))
    base, res = evaluate_repos(t)
    print(f"{len(t)} repos, mean first-timer rate {base:.3f}")
    for name, r in res.items():
        print(name, r)
    for lang, g in t.groupby("language"):
        if len(g) >= 15:
            corr = {c: round(g[c].corr(g["truth"], method="spearman"), 3) for c in res}
            print(lang, len(g), corr)


if __name__ == "__main__":
    main()