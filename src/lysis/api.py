"""FastAPI backend: uvicorn lysis.api:app --reload"""

import os
from functools import lru_cache
from typing import Annotated, Any

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from lysis.cli import rank_repo
from lysis.explain import explain_issue
from lysis.feedback import log_feedback
from lysis.ingestion.github_client import GitHubClient, RateLimitError
from lysis.limits import SlidingWindow, TTLCache
from lysis.models.artifact import load_meta, load_model

load_dotenv()
app = FastAPI(title="Lysis", version="0.1.0")
ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_methods=["GET", "HEAD", "POST"],
    allow_headers=["*"],
)
REPO = r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$"
PER_IP = SlidingWindow(int(os.getenv("RATE_PER_IP", "30")))
GLOBAL = SlidingWindow(int(os.getenv("RATE_GLOBAL", "300")))
CACHE = TTLCache(ttl=600)
FEEDBACK = SlidingWindow(int(os.getenv("RATE_FEEDBACK", "60")))


class Vote(BaseModel):
    repo: str = Field(pattern=REPO)
    issue_number: int = Field(ge=1)
    score: float = Field(ge=0, le=1)
    helpful: bool
    model_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")


def client_ip(request: Request):
    # The right-most entry is added by Render's proxy, so a client can't spoof it.
    fwd = request.headers.get("x-forwarded-for", "")
    if fwd:
        return fwd.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


def limit_ip(request: Request):
    if not PER_IP.allow(client_ip(request)):
        raise HTTPException(
            429, "Too many requests, try again later.", headers={"Retry-After": "60"}
        )

def limit_feedback(request: Request):
    if not FEEDBACK.allow(client_ip(request)):
        raise HTTPException(
            429, "Too many votes, try again later.", headers={"Retry-After": "60"}
        )
        
@lru_cache(maxsize=1)
def _model():
    return load_model(), load_meta()


def get_model():
    return _model()


def get_gh():
    return GitHubClient()


@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/docs")


@app.get("/model")
def model_info(m: Annotated[Any, Depends(get_model)]):
    return m[1]


@app.get("/rank", dependencies=[Depends(limit_ip)])
def rank(
    repo: Annotated[str, Query(pattern=REPO)],
    gh: Annotated[Any, Depends(get_gh)],
    m: Annotated[Any, Depends(get_model)],
    top: Annotated[int, Query(ge=1, le=30)] = 10,
    explain: bool = False,
):
    key = (repo.lower(), top, explain)
    cached = CACHE.get(key)
    if cached is not None:
        return cached
    if not GLOBAL.allow("all"):
        raise HTTPException(
            429, "The service is busy, try again in a few minutes.", headers={"Retry-After": "300"}
        )
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
    result = {"repo": repo, "model_date": m[1]["trained_at"][:10], "issues": rows}
    CACHE.set(key, result)
    return result

@app.post("/feedback", status_code=201, dependencies=[Depends(limit_feedback)])
def feedback(vote: Vote):
    ok = log_feedback(
        vote.repo, vote.issue_number, vote.score, vote.helpful, vote.model_date
    )
    if not ok:
        raise HTTPException(502, "Could not save feedback")
    return {"saved": True}