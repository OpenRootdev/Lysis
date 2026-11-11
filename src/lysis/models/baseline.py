"""Labels-only baseline: good first issue / help wanted + freshness."""

import pandas as pd

LABEL_WEIGHTS = {"good first issue": 2.0, "help wanted": 1.0}


def labels_only_ranker(df, now=None, half_life_days=90):
    now = pd.Timestamp(now) if now is not None else pd.Timestamp.now(tz="UTC")
    age = (now - pd.to_datetime(df["created_at"], utc=True)).dt.days.clip(lower=0)
    freshness = 0.5 ** (age / half_life_days)
    label_score = df["labels"].apply(lambda ls: sum(LABEL_WEIGHTS.get(x, 0) for x in ls))
    return (label_score + freshness).tolist()


def rank_issues(df, **kwargs):
    out = df.copy()
    out["score"] = labels_only_ranker(out, **kwargs)
    return out.sort_values("score", ascending=False).reset_index(drop=True)