import collections
import glob
import json

files = glob.glob("data/raw/*.json")
tot = collections.Counter()
assoc = collections.Counter()
repos_with_first = 0
for f in files:
    d = json.load(open(f))
    tot["open"] += len(d["open_issues"])
    tot["closed"] += len(d["closed_issues"])
    tot["merged_prs"] += len(d["merged_prs"])
    firsts = 0
    for p in d["merged_prs"]:
        assoc[p["author_association"]] += 1
        if p["author_association"] in ("FIRST_TIME_CONTRIBUTOR", "FIRST_TIMER"):
            firsts += 1
    repos_with_first += firsts > 0
print(len(files), "repos;", dict(tot))
print(dict(assoc))
print(repos_with_first, "repos have a first-timer merged PR")