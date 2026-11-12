from lysis.models.gbm import make_gbm_ranker


def test_gbm_ranker_scores(issues_df):
    scores = make_gbm_ranker(issues_df)(issues_df)
    assert len(scores) == len(issues_df)
    assert scores[0] > scores[1]