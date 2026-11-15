"""FastAPI backend: uvicorn lysis.api:app --reload"""

from functools import lru_cache
from typing import Annotated, Any

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse

from lysis.cli import rank_repo
from lysis.explain import explain_issue
from lysis.ingestion.github_client import GitHubClient, RateLimitError
from lysis.models.artifact import load_meta, load_model

load_dotenv()
app = FastAPI(title="Lysis", version="0.1.0")
REPO = r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$"


@lru_cache(maxsize=1)
def _model():
    return load_model(), load_meta()


def get_model():
    return _model()


def get_gh():
    return GitHubClient()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/docs")


@app.get("/model")
def model_info(m: Annotated[Any, Depends(get_model)]):
    return m[1]

@app.get("/model")
def model_info(m: Annotated[Any, Depends(get_model)]):
    return m[1]


@app.get("/rank")
def rank(
    repo: Annotated[str, Query(pattern=REPO)],
    gh: Annotated[Any, Depends(get_gh)],
    m: Annotated[Any, Depends(get_model)],
    top: Annotated[int, Query(ge=1, le=30)] = 10,
    explain: bool = False,
):
    try:
        out = rank_repo(gh, repo, m[0], top)
    except RateLimitError as e:
        raise HTTPException(429, str(e)) from e
    except httpx.HTTPStatusError as e:
        code = 404 if e.response.status_code == 404 else 502
        raise HTTPException(code, f"GitHub error {e.response.status_code}") from e
    except httpx.HTTPError as e:
        raise HTTPException(502, "GitHub unreachable") from e
    rows = out.drop(columns=["body"]).to_dict("records")
    if explain:
        for row, body in zip(rows[:5], out["body"].tolist(), strict=False):
            row["why"] = explain_issue(row["full_title"], body)
    return {"repo": repo, "model_date": m[1]["trained_at"][:10], "issues": rows}