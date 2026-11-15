"""Log thumbs up/down on recommendations to Supabase (insert-only)."""

import os

import httpx


def log_feedback(repo, number, score, helpful, model_date, http=None):
    url, key = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY")
    if not (url and key):
        return False
    row = {
        "repo": repo,
        "issue_number": int(number),
        "score": float(score),
        "helpful": bool(helpful),
        "model_date": model_date,
    }
    headers = {"apikey": key, "Content-Type": "application/json", "Prefer": "return=minimal"}
    if key.startswith("eyJ"):
        headers["Authorization"] = f"Bearer {key}"
    try:
        r = (http or httpx).post(f"{url}/rest/v1/feedback", json=row, headers=headers, timeout=15)
        r.raise_for_status()
        return True
    except httpx.HTTPError:
        return False