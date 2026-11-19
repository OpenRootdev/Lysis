
"""Discover Python repos and save raw issues/PRs to data/raw/."""

import argparse
import json
from datetime import date, time, timedelta
from pathlib import Path

import httpx
from dotenv import load_dotenv

from lysis.config import CATALOG_LANGUAGES, TRAIN_LANGUAGES
from lysis.ingestion.github_client import GitHubClient

BANDS = ["50..300", "300..2000", "2000..20000"]
OUT = Path("data/raw")


def discover(gh, per_band=100, language="python"):
    since = (date.today() - timedelta(days=90)).isoformat()
    repos = []

    for band in BANDS:
        q = (
            f'language:"{language}" stars:{band} '
            f'pushed:>{since} good-first-issues:>2 archived:false'
        )
        data = gh.get(
            "/search/repositories",
            {"q": q, "sort": "updated", "per_page": per_band},
        )
        repos += [r["full_name"] for r in data["items"]]

    return repos


def fetch_repo(gh, full_name, catalog_only=False):
    owner, repo = full_name.split("/")

    prs = gh.get(
        f"/repos/{full_name}/pulls",
        {"state": "closed", "per_page": 100},
    )

    return {
        "repo": gh.get(f"/repos/{full_name}"),
        "open_issues": gh.list_issues(owner, repo, state="open"),
        "closed_issues": (
            [] if catalog_only
            else gh.list_issues(owner, repo, state="closed")
        ),
        "merged_prs": [p for p in prs if p.get("merged_at")],
    }

def is_stale(path, days):
    return days is not None and time.time() - path.stat().st_mtime > days * 86400


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", default="python", help="a language, or 'all'")
    parser.add_argument("--catalog-only", action="store_true")
    parser.add_argument("--refresh-days", type=float, default=None)
    args = parser.parse_args()
    load_dotenv()
    gh = GitHubClient()
    OUT.mkdir(parents=True, exist_ok=True)
    langs = CATALOG_LANGUAGES if args.language == "all" else [args.language]
    for lang in langs:
        catalog_only = args.catalog_only or lang not in TRAIN_LANGUAGES
        for name in discover(gh, language=lang):
            path = OUT / f"{name.replace('/', '__')}.json"
            exists = path.exists()
            if exists and not is_stale(path, args.refresh_days):
                continue
            try:
                data = fetch_repo(gh, name, catalog_only)
            except httpx.HTTPError as e:
                print("skipped", name, e)
                continue
            if exists and catalog_only:
                data["closed_issues"] = json.loads(path.read_text())["closed_issues"]
            path.write_text(json.dumps(data))
            print("saved", name, lang)

if __name__ == "__main__":
    main()
