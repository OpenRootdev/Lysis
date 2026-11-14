"""Minimal GitHub REST client with ETag caching and rate-limit handling."""

import hashlib
import json
import os
import time
from pathlib import Path

import httpx

API = "https://api.github.com"


class RateLimitError(Exception):
    pass


class GitHubClient:
    def __init__(self, token=None, cache_dir="data/cache", client=None, max_wait=None):
        token = token or os.getenv("GITHUB_TOKEN")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        if max_wait is None:
            max_wait = int(os.getenv("LYSIS_MAX_WAIT", "120"))
        self.max_wait = max_wait
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.http = client or httpx.Client(base_url=API, headers=headers, timeout=30)

    def _cache_file(self, path, params):
        raw = f"{path}?{sorted((params or {}).items())}"
        return self.cache_dir / f"{hashlib.sha256(raw.encode()).hexdigest()}.json"

    @staticmethod
    def _limited(resp):
        if resp.status_code not in (403, 429):
            return False
        return resp.headers.get("X-RateLimit-Remaining") == "0" or "Retry-After" in resp.headers

    def _wait(self, resp):
        if "Retry-After" in resp.headers:
            wait = int(resp.headers["Retry-After"])
        else:
            wait = int(resp.headers.get("X-RateLimit-Reset", 0)) - time.time() + 1
        if wait > self.max_wait:
            raise RateLimitError(f"Rate limited; reset in {int(wait)}s")
        time.sleep(max(wait, 0))

    def get(self, path, params=None, retries=3):
        cache_file = self._cache_file(path, params)
        cached = json.loads(cache_file.read_text()) if cache_file.exists() else None
        headers = {"If-None-Match": cached["etag"]} if cached else {}
        for _ in range(retries):
            resp = self.http.get(path, params=params, headers=headers)
            if self._limited(resp):
                self._wait(resp)
                continue
            if resp.status_code == 304 and cached:
                return cached["body"]
            resp.raise_for_status()
            body = resp.json()
            if etag := resp.headers.get("ETag"):
                cache_file.write_text(json.dumps({"etag": etag, "body": body}))
            return body
        raise RateLimitError("Still rate limited after retries")

    def list_issues(self, owner, repo, labels=None, max_pages=3, state="open"):
        """Issues for a repo, excluding pull requests."""
        issues = []
        for page in range(1, max_pages + 1):
            params = {"state": state, "per_page": 100, "page": page}
            if labels:
                params["labels"] = labels
            batch = self.get(f"/repos/{owner}/{repo}/issues", params)
            issues += [i for i in batch if "pull_request" not in i]
            if len(batch) < 100:
                break
        return issues