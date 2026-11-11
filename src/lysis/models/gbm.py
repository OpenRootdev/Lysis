"""Gradient boosting ranker trained on first-timer labels."""

from sklearn.ensemble import GradientBoostingClassifier

from lysis.features.issue_features import build_features


def make_gbm_ranker(train, seed=42):
    model = GradientBoostingClassifier(
        n_estimators=100, max_depth=2, learning_rate=0.1, random_state=seed
    )
    model.fit(build_features(train), train["first_timer"])

    def ranker(df):
        return model.predict_proba(build_features(df))[:, 1]

    return ranker