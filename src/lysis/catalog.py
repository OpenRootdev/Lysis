
"""Build the repo catalog: score open issues with the model, aggregate to repo level."""

import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from lysis.config import VALIDATED_LANGUAGES as VALIDATED
from lysis.features.rows import issue_row, merged_times
from lysis.models.artifact import load_meta, load_model

CATALOG_PATH = Path("models/catalog.json")
MIN_OPEN = 3

# Minimum merged PRs in the last 90 days for a repo to count as active, per level.
ACTIVITY_GATE = {"beginner": 5, "intermediate": 3, "advanced": 1}


def score_repo(d, ranker, as_of, half_life_days=365, top=5):
    r = d["repo"]
    issues = [i for i in d["open_issues"] if not i.get("assignees")]

    if len(issues) < MIN_OPEN:
        return None

    merged = merged_times(d["merged_prs"])
    df = pd.DataFrame([issue_row(i, r, merged) for i in issues])

    age = (
        as_of - pd.to_datetime(df["created_at"], utc=True)
    ).dt.days.clip(lower=0)

    scores = np.asarray(ranker(df)) * 0.5 ** (age / half_life_days)

    lang = (r.get("language") or "").lower()

    return {
        "repo": r["full_name"],
        "url": r["html_url"],
        "description": (r.get("description") or "")[:200],
        "language": lang,
        "validated": lang in VALIDATED,
        "stars": r["stargazers_count"],
        "size_kb": r["size"],
        "open_issues": len(issues),
        "good_first_issues": int(
            sum("good first issue" in ls for ls in df["labels"])
        ),
        "prs_90d": sum((as_of - m).days <= 90 for m in merged),
        "score": round(float(np.sort(scores)[::-1][:top].mean()), 4),
        "as_of": as_of.date().isoformat(),
    }


def assign_levels(repos):
    """Level comes from repo size (a proxy for complexity); activity decides if it is active."""

    sizes = np.array([r["size_kb"] for r in repos], dtype=float)
    p33, p75 = np.percentile(sizes, [33, 75])

    for r in repos:
        if r["size_kb"] <= p33:
            r["level"] = "beginner"
        elif r["size_kb"] <= p75:
            r["level"] = "intermediate"
        else:
            r["level"] = "advanced"

        r["active"] = r["prs_90d"] >= ACTIVITY_GATE[r["level"]]

    return {"p33_kb": float(p33), "p75_kb": float(p75)}


def build_catalog(raw_dir="data/raw", out=CATALOG_PATH):
    ranker, meta = load_model(), load_meta()
    repos = []

    for path in sorted(Path(raw_dir).glob("*.json")):
        # The file time is when the data was fetched, so activity is measured from then.
        as_of = pd.Timestamp(path.stat().st_mtime, unit="s", tz="UTC")

        entry = score_repo(
            json.loads(path.read_text()),
            ranker,
            as_of,
        )

        if entry:
            repos.append(entry)

    thresholds = assign_levels(repos)

    repos.sort(key=lambda r: -r["score"])

    out.parent.mkdir(parents=True, exist_ok=True)

    catalog = {
        "meta": {
            "built_at": datetime.now(UTC).isoformat(),
            "model_date": meta["trained_at"][:10],
            "thresholds": thresholds,
            "n_repos": len(repos),
        },
        "repos": repos,
    }

    out.write_text(json.dumps(catalog, indent=1))

    return catalog


def load_catalog(path=CATALOG_PATH):
    """The only place that knows where the catalog lives. Swap this to move to a database."""

    if not path.exists():
        raise FileNotFoundError(
            "No catalog found. Run: python src/lysis/catalog.py"
        )

    return json.loads(path.read_text())


def main():
    cat = build_catalog()
    df = pd.DataFrame(cat["repos"])

    print(cat["meta"]["n_repos"], "repos;", int(df["active"].sum()), "active")
    print(df.groupby(["language", "level"])["active"].agg(["size", "sum"]))

    cols = ["repo", "language", "level", "score", "size_kb", "prs_90d"]

    print(df[df["active"]].head(10)[cols].to_string(index=False))


if __name__ == "__main__":
    main()
