"""Rank a repo's open issues: python src\\lysis\\cli.py owner/repo [top]"""
import argparse

import pandas as pd
from dotenv import load_dotenv

from lysis.explain import explain_issue
from lysis.features.issue_features import build_features
from lysis.features.rows import issue_row, merged_times
from lysis.ingestion.github_client import GitHubClient
from lysis.models.artifact import load_model

SHOW = ["score", "number", "title", "url"]


def _insights(full, n_open, drivers, repo, merged):
    now = pd.Timestamp.now(tz="UTC")
    ms = pd.to_datetime(list(merged), utc=True) if len(merged) else pd.DatetimeIndex([], tz="UTC")
    feats = build_features(full)
    return {
        "n_open": n_open,
        "n_scored": len(full),
        "n_gfi": int(feats["gfi"].sum()) if "gfi" in feats.columns else 0,
        "median_score": round(float(full["score"].median()), 3),
        "context": {
            "repo_age_days": int((now - pd.to_datetime(repo["created_at"], utc=True)).days),
            "merged_90d": int(((now - ms) <= pd.Timedelta(days=90)).sum()),
            "days_since_merge": int((now - ms.max()).days) if len(ms) else None,
        },
        "drivers": drivers,
    }


def rank_repo(gh, full_name, ranker, top=10, half_life_days=365, insights=False):
    owner, name = full_name.split("/")

    repo = gh.get(f"/repos/{full_name}")
    prs = gh.get(
        f"/repos/{full_name}/pulls",
        {"state": "closed", "per_page": 100},
    )
    merged = merged_times(prs)

    open_issues = gh.list_issues(owner, name, state="open")
    issues = [i for i in open_issues if not i.get("assignees")]

    cols = [*SHOW, "full_title", "body"]

    if not issues:
        return pd.DataFrame(columns=cols)

    df = pd.DataFrame([issue_row(i, repo, merged) for i in issues])
    df["body"] = [(i.get("body") or "")[:1500] for i in issues]
    df["score"] = list(ranker(df))

    age = (
        pd.Timestamp.now(tz="UTC")
        - pd.to_datetime(df["created_at"], utc=True)
    ).dt.days

    df["score"] = df["score"] * 0.5 ** (
        age.clip(lower=0) / half_life_days
    )

    full = df
    df = df.sort_values("score", ascending=False).head(top)

    drivers = (
        ranker.explain(full, df.index.tolist())
        if insights and hasattr(ranker, "explain")
        else []
    )

    df["number"] = df["issue_number"]
    df["full_title"] = df["title"]
    df["title"] = df["title"].str[:60]
    df["score"] = df["score"].round(3)

    out = df[cols]

    if insights:
        out.attrs["insights"] = _insights(full, len(open_issues), drivers, repo, merged)

    return out


def main():
    load_dotenv()

    p = argparse.ArgumentParser()
    p.add_argument("repo")
    p.add_argument("top", nargs="?", type=int, default=10)
    p.add_argument("--explain", action="store_true")
    a = p.parse_args()

    out = rank_repo(
        GitHubClient(),
        a.repo,
        load_model(),
        a.top,
    )

    print(out[SHOW].to_string(index=False))

    if a.explain:
        for _, r in out.head(5).iterrows():
            note = (
                explain_issue(r["full_title"], r["body"])
                or "n/a (check GROQ_API_KEY)"
            )
            print(f"\n#{r['number']}: {note}")


if __name__ == "__main__":
    main()