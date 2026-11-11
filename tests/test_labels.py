from lysis.features.labels import linked_issues


def test_linked_issues():
    pr = {"body": "Fixes #12 and closes: #34. See #99."}
    assert linked_issues(pr) == {12, 34}