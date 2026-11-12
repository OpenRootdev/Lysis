"""Gradient boosting ranker on tabular issue and repo features."""

from sklearn.ensemble import HistGradientBoostingClassifier

from lysis.features.issue_features import FEATURE_COLUMNS, build_features


def make_gbm_ranker(train, seed=42, drop=()):
    cols = [c for c in FEATURE_COLUMNS if c not in drop]
    model = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.1, random_state=seed)
    model.fit(build_features(train)[cols], train["first_timer"])

    def ranker(df):
        return model.predict_proba(build_features(df)[cols])[:, 1]

    return ranker