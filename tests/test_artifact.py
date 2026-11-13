import pandas as pd

from lysis.models.artifact import load_meta, load_model, save_model
from lysis.models.gbm import make_gbm_ranker


def test_save_load_roundtrip(issues_df, tmp_path):
    big = pd.concat([issues_df] * 10, ignore_index=True)
    ranker = make_gbm_ranker(big)
    path = tmp_path / "m.joblib"
    save_model(ranker, {"n_train": len(big)}, path)
    assert list(load_model(path)(big)) == list(ranker(big))
    assert load_meta(path)["n_train"] == len(big)