"""Issue and repo features. Only data visible when the issue was opened."""

import numpy as np
import pandas as pd

LABEL_FLAGS = {
    "gfi": "good first issue",
    "help_wanted": "help wanted",
    "bug": "bug",
    "docs": "documentation",
    "enhancement": "enhancement",
}
MAINTAINER_ASSOC = ["OWNER", "MEMBER", "COLLABORATOR"]

FEATURE_COLUMNS = [
    *LABEL_FLAGS,
    "n_labels",
    "body_len_log",
    "title_len",
    "has_code",
    "is_maintainer",
    "stars_log",
    "forks_log",
    "repo_size_log",
    "has_license",
    "repo_age_days",
]


def build_features(df):
    out = pd.DataFrame(index=df.index)
    for name, label in LABEL_FLAGS.items():
        out[name] = df["labels"].apply(lambda ls, lab=label: int(lab in ls))
    out["n_labels"] = df["labels"].apply(len)
    out["body_len_log"] = np.log1p(df["body_len"])
    out["title_len"] = df["title_len"]
    out["has_code"] = df["has_code"]
    out["is_maintainer"] = df["author_assoc"].isin(MAINTAINER_ASSOC).astype(int)
    out["stars_log"] = np.log1p(df["stars"])
    out["forks_log"] = np.log1p(df["forks"])
    out["repo_size_log"] = np.log1p(df["repo_size"])
    out["has_license"] = df["has_license"]
    age = pd.to_datetime(df["created_at"], utc=True) - pd.to_datetime(
        df["repo_created_at"], utc=True
    )
    out["repo_age_days"] = age.dt.days
    return out[FEATURE_COLUMNS]