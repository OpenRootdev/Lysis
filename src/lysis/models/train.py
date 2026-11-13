"""Train on all data, report CV, save the artifact."""

from lysis.models.artifact import save_model
from lysis.models.evaluate import cross_validate, load_dataset
from lysis.models.gbm import make_gbm_ranker


def main():
    df = load_dataset()
    cv = cross_validate(df, {"gbm": make_gbm_ranker})["gbm"]
    save_model(
        make_gbm_ranker(df),
        {"n_train": len(df), "base_rate": round(float(df["first_timer"].mean()), 3), "cv": cv},
    )
    print("saved models/gbm.joblib", cv)


if __name__ == "__main__":
    main()