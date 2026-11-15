"""Thin client for the hosted Lysis API."""

import httpx


class ApiError(Exception):
    pass


def _get(base, path, params=None, http=None, timeout=90):
    try:
        r = (http or httpx).get(f"{base.rstrip('/')}{path}", params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.json().get("detail", "")
        except ValueError:
            detail = ""
        raise ApiError(f"API error {e.response.status_code}: {detail}".strip()) from e
    except httpx.HTTPError as e:
        raise ApiError("API unreachable. It may be waking up, try again in a minute.") from e
    except ValueError as e:
        raise ApiError("Unexpected API response.") from e


def fetch_model(base, http=None):
    return _get(base, "/model", http=http)


def fetch_rank(base, repo, top, explain=True, http=None):
    params = {"repo": repo, "top": top, "explain": str(explain).lower()}
    return _get(base, "/rank", params, http=http)