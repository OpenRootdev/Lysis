# Label definition: beginner-friendly

An issue is a positive example (first_timer = 1) if it was closed by a merged PR
whose author had no commits in that repo before the PR was opened. Otherwise it is
a negative (first_timer = 0).

Method: PRs link issues via closing keywords (fixes/closes/resolves #N). Bot authors
are excluded. First-timer status uses the repo commit history before the PR's creation
date, because GitHub rewrites FIRST_TIME_CONTRIBUTOR to CONTRIBUTOR after merge.

Current data: 994 labeled issues, 210 positives (about 21%).

Known limits:
- Measures "a newcomer resolved it", an approximation of beginner-friendly.
- Issues no newcomer attempted are never labeled positive.
- One PR closing several issues counts each issue separately.
- Sample is 73 Python repos; results may not transfer to other languages.