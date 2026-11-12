"""Build one model-input row from a GitHub issue and its repo."""


def issue_row(issue, repo):
    body = issue.get("body") or ""
    return {
        "repo": repo["full_name"],
        "issue_number": issue["number"],
        "title": issue.get("title") or "",
        "url": issue.get("html_url", ""),
        "labels": [x["name"].lower() for x in issue["labels"]],
        "comments": issue["comments"],
        "body_len": len(body),
        "title_len": len(issue.get("title") or ""),
        "has_code": int("```" in body),
        "author_assoc": issue.get("author_association") or "NONE",
        "stars": repo["stargazers_count"],
        "forks": repo["forks_count"],
        "repo_size": repo["size"],
        "has_license": int(bool(repo.get("license"))),
        "repo_created_at": repo["created_at"],
        "created_at": issue["created_at"],
    }