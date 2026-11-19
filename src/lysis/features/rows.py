"""Build one model-input row. Repo activity uses only PRs merged before the issue."""

import re

import pandas as pd


def merged_times(prs):
    return [pd.Timestamp(p["merged_at"]) for p in prs if p.get("merged_at")]


def pr_activity(merged, at):
    at = pd.Timestamp(at)
    before = [m for m in merged if m < at]
    return {
        "prs_90d": sum((at - m).days <= 90 for m in before),
        "merge_gap_days": (at - max(before)).days if before else 999,
    }
    
GFI = {
    "good first issue", "good first bug", "good first contribution", "first timers only",
    "beginner", "beginner friendly", "good for beginners", "good for newcomers", "newcomer",
    "easy", "easy fix", "e easy", "difficulty easy", "difficulty beginner", "up for grabs",
    "low hanging fruit",
}
HELP = {
    "help wanted", "help welcome", "contributions welcome", "contribution welcome",
    "pr welcome", "prs welcome", "pull request welcome", "status help wanted",
}


def norm_labels(raw):
    names = [x["name"].lower() for x in raw]
    out = list(names)
    for n in names:
        k = re.sub(r"[\s_:-]+", " ", n).strip()
        if k in GFI and "good first issue" not in out:
            out.append("good first issue")
        if k in HELP and "help wanted" not in out:
            out.append("help wanted")
    return out


def issue_row(issue, repo, merged):
    body = issue.get("body") or ""
    return {
        "repo": repo["full_name"],
        "issue_number": issue["number"],
        "title": issue.get("title") or "",
        "url": issue.get("html_url", ""),
        "labels": norm_labels(issue["labels"]),
        "comments": issue["comments"],
        "body_len": len(body),
        "title_len": len(issue.get("title") or ""),
        "has_code": int("```" in body),
        "author_assoc": issue.get("author_association") or "NONE",
        "has_license": int(bool(repo.get("license"))),
        "language": (repo.get("language") or "").lower(),
        "repo_created_at": repo["created_at"],
        "created_at": issue["created_at"],
        **pr_activity(merged, issue["created_at"]),
    }