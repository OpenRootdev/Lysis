"""Rank a repo's open issues: python src\\lysis\\cli.py owner/repo [top]"""

import sys

import pandas as pd
from dotenv import load_dotenv

from lysis.features.rows import issue_row
from lysis.ingestion.github_client import GitHubClient
from lysis.models.evaluate import load_dataset
from lysis.models.gbm import make_gbm_ranker


def rank_repo(gh, full_name, ranker, top=10):
    owner, name = full_name.split("/")
    repo = gh.get(f"/repos/{full_name}")
    issues = [i for i in gh.list_issues(owner, name, state="open") if not i.get("assignees")]
    if not issues:
        return pd.DataFrame(columns=["score", "number", "title", "url"])
    df = pd.DataFrame([issue_row(i, repo) for i in issues])
    df["score"] = list(ranker(df))
    df = df.sort_values("score", ascending=False).head(top)
    df["number"] = df["issue_number"]
    df["title"] = df["title"].str[:60]
    df["score"] = df["score"].round(3)
    return df[["score", "number", "title", "url"]]


def main():
    load_dotenv()
    if len(sys.argv) < 2:
        sys.exit("usage: python src\\lysis\\cli.py owner/repo [top]")
    top = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    ranker = make_gbm_ranker(load_dataset())
    print(rank_repo(GitHubClient(), sys.argv[1], ranker, top).to_string(index=False))


if __name__ == "__main__":
    main()