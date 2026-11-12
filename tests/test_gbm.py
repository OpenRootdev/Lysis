import pandas as pd

from lysis.models.gbm import make_gbm_ranker


def test_gbm_ranker_scores(issues_df):
    big = pd.concat([issues_df] * 10, ignore_index=True)
    scores = make_gbm_ranker(big)(big)
    assert len(scores) == len(big)
    assert scores[0] > scores[1]