"""Train on all data, report CV, save the artifact."""

from sklearn.inspection import permutation_importance

from lysis.features.issue_features import build_features
from lysis.models.artifact import save_model
from lysis.models.evaluate import cross_validate, load_dataset
from lysis.models.gbm import make_gbm_ranker


def main():
    df = load_dataset()
    cv = cross_validate(df, {"gbm": make_gbm_ranker})["gbm"]
    ranker = make_gbm_ranker(df)
    imp = permutation_importance(
        ranker.model,
        build_features(df)[ranker.cols],
        df["first_timer"],
        scoring="average_precision",
        n_repeats=5,
        random_state=42,
    )
    pairs = sorted(zip(ranker.cols, imp.importances_mean.round(4).tolist()), key=lambda t: -t[1])
    save_model(
        ranker,
        {
            "n_train": len(df),
            "base_rate": round(float(df["first_timer"].mean()), 3),
            "cv": cv,
            "importance": dict(pairs[:8]),
        },
    )
    print("saved models/gbm.joblib", cv)
    print(pairs[:8])


if __name__ == "__main__":
    main()