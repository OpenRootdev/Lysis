# Lysis

Beginner-friendly GitHub issue ranker. Give it a repo and it ranks the open issues by how likely a first-time contributor is to get a PR merged for them.

Labels like `good first issue` are often stale or wrong, so Lysis learns from what actually happened: issues that first-time contributors really closed.

**Live demo:** https://mcx78yh52appm5botjqrh52.streamlit.app/

## How it works

1. **Ingest:** fetch repos, issues and merged PRs from the GitHub API (ETag-cached).
2. **Label:** an issue is positive if a first-time contributor's PR closing it was merged.
3. **Model:** gradient boosting on issue and repo features, evaluated with repo-grouped cross-validation.
4. **Rank:** score open, unassigned issues, then decay by age so stale issues sink.

## Results

5-fold repo-grouped CV on closed issues (base rate 0.10):

| Ranker | AP | AUC |
|---|---|---|
| random | ~0.10 | 0.50 |
| labels-only baseline | 0.245 | 0.678 |
| gradient boosting | 0.278 | 0.753 |

This is an early prototype. The model beats the baseline, but the signal is modest.

## Quick start

```bash
git clone https://github.com/OpenRootdev/Lysis.git
cd Lysis
python -m venv .venv
.venv\Scripts\activate        # Windows (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
cp .env.example .env          # add a read-only GITHUB_TOKEN
```

Build the dataset (once, takes a while, cached):

```bash
python src/lysis/ingestion/fetch.py
python src/lysis/features/labels.py
python src/lysis/models/evaluate.py
```

Rank issues:

```bash
python src/lysis/cli.py psf/requests
streamlit run src/lysis/app.py
```

## Project layout

```
src/lysis/
  ingestion/   GitHub client and repo fetching
  features/    labels and feature building
  models/      baseline, gradient boosting, evaluation
  cli.py       command line ranking
  app.py       Streamlit UI
tests/
```

## Known limitations

- Repo stats come from fetch time, not issue time (a small leak; removing them costs about 0.025 AP).
- Only Python repos so far.
- Labels depend on PRs linking issues with `closes #N`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Look for issues labeled `good first issue`.

