"""Discover Python repos and save raw issues/PRs to data/raw/."""

import json
from datetime import date, timedelta
from pathlib import Path

import httpx
from dotenv import load_dotenv

from lysis.ingestion.github_client import GitHubClient

BANDS = ["50..300", "300..2000", "2000..20000"]
OUT = Path("data/raw")


def discover(gh, per_band=100):
    since = (date.today() - timedelta(days=90)).isoformat()
    repos = []
    for band in BANDS:
        q = f"language:python stars:{band} pushed:>{since} good-first-issues:>2 archived:false"
        data = gh.get("/search/repositories", {"q": q, "sort": "updated", "per_page": per_band})
        repos += [r["full_name"] for r in data["items"]]
    return repos


def fetch_repo(gh, full_name):
    owner, repo = full_name.split("/")
    prs = gh.get(f"/repos/{full_name}/pulls", {"state": "closed", "per_page": 100})
    return {
        "repo": gh.get(f"/repos/{full_name}"),
        "open_issues": gh.list_issues(owner, repo, state="open"),
        "closed_issues": gh.list_issues(owner, repo, state="closed"),
        "merged_prs": [p for p in prs if p.get("merged_at")],
    }


def main():
    load_dotenv()
    gh = GitHubClient()
    OUT.mkdir(parents=True, exist_ok=True)
    for name in discover(gh):
        path = OUT / f"{name.replace('/', '__')}.json"
        if path.exists():
            continue
        try:
            path.write_text(json.dumps(fetch_repo(gh, name)))
        except httpx.HTTPError as e:
            print("skipped", name, e)
            continue
        print("saved", name)


if __name__ == "__main__":
    main()