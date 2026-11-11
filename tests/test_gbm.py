import pandas as pd

from lysis.models.gbm import make_gbm_ranker


def test_gbm_ranker_scores():
    df = pd.DataFrame(
        {
            "labels": [["good first issue"], [], ["good first issue"], ["bug"]] * 5,
            "body_len": [50, 10, 80, 200] * 5,
            "first_timer": [1, 0, 1, 0] * 5,
        }
    )
    scores = make_gbm_ranker(df)(df)
    assert len(scores) == len(df)
    assert scores[0] > scores[1]