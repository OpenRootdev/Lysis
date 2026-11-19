"""Does the model transfer across languages? Train on one language, test on another."""

from lysis.features.issue_features import LANGUAGES
from lysis.models.baseline import labels_only_ranker
from lysis.models.evaluate import evaluate, load_dataset
from lysis.models.gbm import make_gbm_ranker

NO_LANG = tuple(f"lang_{lang}" for lang in LANGUAGES)


def enough(df, lang, n):
    return (df["language"] == lang).sum() >= n


def transfer(df, src, dst):
    train, test = df[df["language"] == src], df[df["language"] == dst]
    ranker = make_gbm_ranker(train, drop=NO_LANG)
    return {
        "n_test": len(test),
        "base": round(float(test["first_timer"].mean()), 3),
        "labels-only": evaluate(labels_only_ranker, test, ks=()),
        "transfer": evaluate(ranker, test, ks=()),
    }


def main():
    df = load_dataset()
    langs = sorted(df["language"].unique())
    for src in langs:
        for dst in langs:
            if src != dst and enough(df, src, 500) and enough(df, dst, 200):
                print(f"{src} -> {dst}", transfer(df, src, dst))


if __name__ == "__main__":
    main()