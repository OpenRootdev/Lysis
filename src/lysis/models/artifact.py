"""Save and load the trained ranker as a versioned artifact."""

import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
import sklearn

MODEL_PATH = Path("models/gbm.joblib")


def save_model(ranker, meta, path=MODEL_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(ranker, path)
    meta = {
        **meta,
        "trained_at": datetime.now(UTC).isoformat(),
        "sklearn": sklearn.__version__,
        "features": ranker.cols,
    }
    path.with_suffix(".json").write_text(json.dumps(meta, indent=2))


def load_model(path=MODEL_PATH):
    if not path.exists():
        raise FileNotFoundError("No model found. Run: python src\\lysis\\models\\train.py")
    return joblib.load(path)


def load_meta(path=MODEL_PATH):
    return json.loads(path.with_suffix(".json").read_text())