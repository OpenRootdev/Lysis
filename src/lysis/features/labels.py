"""Build first-timer labels from raw data into data/labels.csv."""

import csv
import json
import re
from pathlib import Path

import httpx
from dotenv import load_dotenv

from lysis.ingestion.github_client import GitHubClient

LINK = re.compile(r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s*:?\s*#(\d+)", re.I)


def linked_issues(pr):
    return {int(n) for n in LINK.findall(pr.get("body") or "")}


def is_first_timer(gh, full_name, login, before):
    """True if the author had no commits in the repo before `before`."""
    params = {"author": login, "until": before, "per_page": 1}
    try:
        return len(gh.get(f"/repos/{full_name}/commits", params)) == 0
    except httpx.HTTPStatusError:
        return False


def main():
    load_dotenv()
    gh = GitHubClient()
    rows = []
    for path in sorted(Path("data/raw").glob("*.json")):
        d = json.loads(path.read_text())
        name = d["repo"]["full_name"]
        closed = {i["number"] for i in d["closed_issues"]}
        for pr in d["merged_prs"]:
            if pr["user"]["type"] == "Bot":
                continue
            issues = linked_issues(pr) & closed
            if not issues:
                continue
            first = int(is_first_timer(gh, name, pr["user"]["login"], pr["created_at"]))
            rows += [(name, n, first) for n in sorted(issues)]
    with open("data/labels.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["repo", "issue_number", "first_timer"])
        w.writerows(rows)
    print(len(rows), "labeled issues;", sum(r[2] for r in rows), "first-timer positives")


if __name__ == "__main__":
    main()