import json

import httpx

from lysis.feedback import log_feedback


def test_log_feedback_posts_row(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://x.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "k")
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        seen["body"] = json.loads(request.content)
        return httpx.Response(201)

    http = httpx.Client(transport=httpx.MockTransport(handler))
    assert log_feedback("a/b", 5, 0.3, True, "2026-11-14", http=http)
    assert seen["url"].endswith("/rest/v1/feedback")
    assert seen["body"]["helpful"] is True and seen["body"]["issue_number"] == 5


def test_log_feedback_without_keys_is_noop(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    assert log_feedback("a/b", 1, 0.1, False, "d") is False


def test_log_feedback_handles_http_error(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://x.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "k")
    http = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(500)))
    assert log_feedback("a/b", 1, 0.1, True, "d", http=http) is False