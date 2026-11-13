# Contributing

1. Pick an issue and comment that you're working on it.
2. Branch from `main`: `git checkout -b feat/short-name`.
3. Set up as in the README, then make your change.
4. Before pushing: `ruff check . --fix` and `pytest` must pass.
5. Open a PR with `Closes #N` in the description. CI must be green.

Keep PRs small and focused. Changes to the model should include evaluation numbers (`python src/lysis/models/evaluate.py`).