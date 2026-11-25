# Contributing to Lysis

Thanks for helping make Lysis better. Contributions of any size are welcome: a typo, a test, a bug fix, a new language, or a model improvement.

By taking part you agree to our [Code of Conduct](CODE_OF_CONDUCT.md) and that your contributions are released under the [MIT License](LICENSE).

## Table of contents

- [Contributing to Lysis](#contributing-to-lysis)
  - [Table of contents](#table-of-contents)
  - [Ways to contribute](#ways-to-contribute)
  - [House rules](#house-rules)
  - [Development setup](#development-setup)
  - [Project layout](#project-layout)
  - [Branches and commits](#branches-and-commits)
  - [Coding standards](#coding-standards)
  - [Testing](#testing)
  - [Model changes](#model-changes)
  - [Adding a language](#adding-a-language)
  - [Making a pull request](#making-a-pull-request)
  - [Priorities](#priorities)
  - [Reporting security issues](#reporting-security-issues)
  - [Troubleshooting](#troubleshooting)

## Ways to contribute

- **Pick up a `good first issue`.** These are small and well scoped. Comment on the issue so nobody duplicates your work.
- **Report a bug.** Include the repository you searched, what you expected, and what you got.
- **Tell us where the ranking is wrong.** If the top picks for a repo you know look off, open an issue. Real examples are the most useful feedback we get.
- **Improve the docs.** Clearer setup steps and better examples are always welcome.
- **Propose a feature or a model change.** Open an issue first (see below).

## House rules

**Check before you start.** Search existing [issues](https://github.com/OpenRootdev/Lysis/issues) and [pull requests](https://github.com/OpenRootdev/Lysis/pulls) so work isn't duplicated.

**Discuss features first.** For a new feature or a model change, open an issue and wait for a maintainer to agree on the direction before you write code. This keeps the product consistent and saves you from a rejected PR. Bug fixes, docs and tests don't need prior approval, so start right away.

**Make issues and PRs stand on their own.** Explain the problem, what you changed, and why. Don't just paste a link to a chat or a ticket. If the idea came from a private conversation, summarise the relevant reasoning, leaving out anything sensitive.

**Think like a reviewer.** What would you want to know reading this for the first time? Link related issues, and note trade-offs, edge cases and any temporary workaround.

**Say how you tested.** A sentence is enough, for example: "Ran `pytest`, and ranked `psf/requests` locally and checked the top five."

**Use closing keywords.** Write `Closes #123` in the PR description so the issue links and closes automatically.

**Never commit secrets.** No tokens, API keys or `.env` files. The repo's history is scanned for leaks.

## Development setup

You need Python 3.13, Node.js 22, and a read-only GitHub token for public repositories. A Groq key and Docker are optional.

```powershell
git clone https://github.com/<your-username>/Lysis.git     # your fork
cd Lysis
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
copy .env.example .env          # macOS/Linux: cp .env.example .env
```

Add `GITHUB_TOKEN` to `.env`. The other variables are in the [README](README.md#configuration).

Run the API and the web app:

```bash
uvicorn lysis.api:app --reload          # http://127.0.0.1:8000, docs at /docs
cd web && npm install && npm run dev    # http://localhost:3000
```

Put `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000` in `web/.env.local`.

## Project layout

```
src/lysis/
  ingestion/   GitHub client and repo fetching
  features/    labels, feature building, label normalisation
  models/      baseline, gradient boosting, evaluation, training
  catalog.py   scored repo catalog
  api.py       FastAPI service
  cli.py       command line ranking
  config.py    languages and validation settings
web/           Next.js app
tests/         Python tests
docs/          documentation
.github/       CI and the weekly refresh workflow
```

## Branches and commits

1. Fork the repository and branch from `main`. Don't commit directly to `main`.
2. Use a short, descriptive branch name: `feat/short-name`, `fix/short-name`, `docs/short-name`, `test/short-name` or `ci/short-name`.
3. Write commit messages as `type: short description`, using `feat`, `fix`, `docs`, `test`, `refactor`, `chore` or `ci`.
4. Keep your branch current with `main` (use the **Update branch** button on the PR, or rebase).

## Coding standards

**Python**
- Format and lint with `ruff check . --fix`. The same check runs in CI.
- Prefer small, pure functions that are easy to test.
- Catch specific exceptions (`httpx.HTTPError`, `ValueError`), never a bare `except Exception`.
- Don't call the GitHub API in tests. Use fakes or `httpx.MockTransport`.
- Features may only use data that was visible when the issue was opened. Anything computed from the future leaks the answer.

**TypeScript and web**
- `npm run lint` and `npm run build` must pass from `web/`.
- Keep the frontend a thin client: the API owns the model, the keys and all writes.
- Never put a secret in a `NEXT_PUBLIC_` variable. It is visible in the browser.
- Keep the UI minimal, keyboard accessible, and readable without colour alone.

## Testing

```powershell
ruff check .
pytest
cd web && npm run lint && npm run build
```

- Add or update tests for every behaviour change. A bug fix needs a test that fails without it.
- Tests must be fast and offline. The suite should run with no token and no network.
- End-to-end tests use Playwright and mock the API, so they run without a backend. If you see `Executable doesn't exist`, run `npx playwright install`.
- CI runs the Python checks, the web lint and build, and a Docker build on every push and pull request. All three must be green before merge.

## Model changes

The model is evaluated, not guessed at, so changes need evidence.

1. Run `python src/lysis/models/evaluate.py` before and after your change.
2. Compare on the repo-grouped cross-validation line (`cv:`) and the per-language lines.
3. Put both sets of numbers in the PR description. A change is kept only if it clearly beats the current model, by roughly 0.01 average precision or more, and doesn't hurt any language.
4. Ideas that didn't help are still valuable. Open a PR or issue describing what you tried so nobody repeats it.
5. Don't upgrade `scikit-learn` casually. The saved model is a pickle tied to its version, so a version change means retraining and committing a new `models/gbm.joblib`.

Fetching data and building labels uses your GitHub token and can take hours. If you hit `RateLimitError`, set `LYSIS_MAX_WAIT=3700` and rerun. Progress is cached.

## Adding a language

1. Add the language name to `CATALOG_LANGUAGES` in `src/lysis/config.py`.
2. Fetch it: `python -m lysis.ingestion.fetch --language <name> --catalog-only`.
3. Rebuild the catalog: `python -m lysis.catalog`.

A new language starts as **unvalidated**. To validate it, backfill closed issues (`--backfill-closed`), run `labels.py` and `evaluate.py`, and add it to `VALIDATED_LANGUAGES` only if the model beats the label baseline on both AP and AUC.

## Making a pull request

**Keep it small and focused.** Aim for under about 500 changed lines and one concern per PR: one feature, one bug fix or one refactor. Split large changes, and do preparatory refactoring in its own PR first. Data files such as `models/catalog.json` and `models/gbm.joblib` don't count toward the limit.

**Checklist**
- [ ] I'm on a branch (not `main`) and it's up to date
- [ ] `ruff check .` and `pytest` pass, and for web changes `npm run lint` and `npm run build` too
- [ ] I added or updated tests
- [ ] For model changes, I included before and after evaluation numbers
- [ ] The description explains what changed, why, and how I tested it, and includes `Closes #N`
- [ ] No secrets, tokens or `.env` files are included
- [ ] I ticked **Allow edits from maintainers**

Maintainers aim to give a first response within a few days. Changes to `main` go through a PR with passing CI, and Dependabot keeps dependencies current.

## Priorities

| Type | Priority |
|---|---|
| Security issues, data leaks in labels or features | Highest |
| Wrong rankings, crashes, broken API or site | High |
| Evaluation correctness, test and CI reliability | High |
| New languages and model improvements backed by numbers | Medium |
| UX polish and documentation | Medium |
| Minor improvements and non-core feature requests | Lower |

## Reporting security issues

Please don't open a public issue for a vulnerability. Email [help@trylysis.me](mailto:help@trylysis.me) with the details, and we'll respond as soon as we can.

## Troubleshooting

- **`RateLimitError`:** set `LYSIS_MAX_WAIT=3700` and rerun. Progress is cached.
- **CORS error in the browser:** `CORS_ORIGINS` must match the site's exact origin, and an old process may still be using port 8000.
- **Model won't load:** the scikit-learn version differs from the one that trained it. Reinstall from `requirements.txt` or retrain.
- **PowerShell blocks `Activate.ps1`:** run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

More answers are in the [README troubleshooting section](README.md#troubleshooting). Questions that don't fit an issue: [help@trylysis.me](mailto:help@trylysis.me).