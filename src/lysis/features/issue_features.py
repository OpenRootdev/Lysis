"""Issue-level features. Only data visible when the issue was opened."""

import numpy as np
import pandas as pd

LABEL_FLAGS = {
    "gfi": "good first issue",
    "help_wanted": "help wanted",
    "bug": "bug",
    "docs": "documentation",
    "enhancement": "enhancement",
}

FEATURE_COLUMNS = [*LABEL_FLAGS, "n_labels", "body_len_log"]


def build_features(df):
    out = pd.DataFrame(index=df.index)
    for name, label in LABEL_FLAGS.items():
        out[name] = df["labels"].apply(lambda ls, lab=label: int(lab in ls))
    out["n_labels"] = df["labels"].apply(len)
    out["body_len_log"] = np.log1p(df["body_len"])
    return out[FEATURE_COLUMNS]