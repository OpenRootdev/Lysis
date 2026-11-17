import pandas as pd

from lysis.models.repo_eval import evaluate_repos, repo_table


def test_repo_table_and_eval():
    rows = [
        {
            "repo": f"r{r}",
            "language": "python",
            "labels": ["good first issue"] if i < r else [],
            "first_timer": int(i < r),
        }
        for r in range(4)
        for i in range(6)
    ]
    df = pd.DataFrame(rows)
    t = repo_table(df, df["first_timer"].astype(float).to_numpy(), min_issues=5)
    assert len(t) == 4
    _, res = evaluate_repos(t, k=2)
    assert res["mean_all"]["spearman"] == 1.0