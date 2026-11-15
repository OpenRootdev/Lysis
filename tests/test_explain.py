import httpx

from lysis.explain import explain_issue


def client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_explain_returns_text():
    def handler(request):
        return httpx.Response(200, json={"choices": [{"message": {"content": " Fix a typo. "}}]})

    assert explain_issue("t", "b", api_key="k", http=client(handler)) == "Fix a typo."


def test_explain_without_key_returns_none(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    assert explain_issue("t", "b") is None


def test_explain_handles_http_error():
    def handler(request):
        return httpx.Response(500)

    assert explain_issue("t", "b", api_key="k", http=client(handler)) is None