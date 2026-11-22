"""Gradient boosting ranker on tabular issue and repo features."""

from sklearn.ensemble import HistGradientBoostingClassifier

from lysis.features.issue_features import FEATURE_COLUMNS, build_features


class GBMRanker:
    def __init__(self, model, cols):
        self.model = model
        self.cols = cols

    def __call__(self, df):
        return self.model.predict_proba(build_features(df)[self.cols])[:, 1]

    def explain(self, df, idx, k=3):
        """Per-issue score drivers versus a typical issue in the same repo."""
        X = build_features(df)[self.cols]
        med = X.median()
        T = X.loc[idx]
        base = self.model.predict_proba(T)[:, 1]
        delta = {}
        for c in self.cols:
            if (T[c] == med[c]).all():
                continue
            Z = T.copy()
            Z[c] = med[c]
            delta[c] = base - self.model.predict_proba(Z)[:, 1]
        out = []
        for i in range(len(T)):
            ranked = sorted(((c, float(d[i])) for c, d in delta.items()), key=lambda t: -abs(t[1]))
            out.append([{"feature": c, "effect": round(v, 3)} for c, v in ranked[:k] if abs(v) > 1e-4])
        return out


def make_gbm_ranker(train, seed=42, drop=()):
    cols = [c for c in FEATURE_COLUMNS if c not in drop]
    model = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.1, random_state=seed)
    model.fit(build_features(train)[cols], train["first_timer"])
    return GBMRanker(model, cols)