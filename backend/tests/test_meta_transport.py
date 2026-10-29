import json

import httpx

from backend.adapters.meta_transport import (
    EXTRACT_MODEL,
    ExtractRequest,
    MetaClient,
    build_extract_schema,
)


def _mock_chat(payload: dict):
    def handler(request: httpx.Request):
        assert request.url.path == "/v1/chat/completions"
        assert request.headers["authorization"].startswith("Bearer LLM_")
        body = json.loads(request.content.decode())
        assert body["model"] == EXTRACT_MODEL
        assert body["response_format"]["type"] == "json_schema"
        return httpx.Response(200, json={
            "choices": [{"message": {"content": json.dumps(payload)}}]})
    return httpx.MockTransport(handler)


def test_complete_sends_json_schema_and_parses():
    payload = {"conditions": [{"term": "rent_amount", "value": 30000,
                               "currency": "KGS", "quote": "аренда 30000 сом",
                               "confidence": 0.9, "hedged": False}]}
    client = MetaClient(api_key="LLM_1_test", transport=_mock_chat(payload))
    out = client.complete(prompt="P", source_text="аренда 30000 сом", timeout=30)
    assert out["conditions"][0]["value"] == 30000


def test_extract_schema_covers_all_terms_strict_subset():
    schema = build_extract_schema()
    cond = schema["properties"]["conditions"]["items"]
    assert set(cond["properties"]["term"]["enum"]) == {
        "rent_amount", "deposit", "term", "utilities", "pets",
        "prepayment", "repairs", "owner_access", "termination", "deposit_return"}
    assert cond.get("additionalProperties") is False


def test_transcribe_posts_multipart_and_returns_text():
    def handler(request: httpx.Request):
        assert request.url.path == "/v1/asr/transcribe"
        assert request.headers["authorization"].startswith("Bearer LLM_")
        assert "multipart/form-data" in request.headers["content-type"]
        return httpx.Response(200, json={"transcript": "аренда 30000 сом",
                                         "turns": []})
    client = MetaClient(api_key="LLM_1_test", transport=httpx.MockTransport(handler))
    text = client.transcribe(audio=b"RIFF....WAVE", timeout=30)
    assert text == "аренда 30000 сом"


def test_ocr_sends_image_url_and_returns_text():
    def handler(request: httpx.Request):
        body = json.loads(request.content.decode())
        content = body["messages"][0]["content"]
        assert any(p.get("type") == "image_url" for p in content)
        return httpx.Response(200, json={
            "choices": [{"message": {"content": "аренда 30000 сом"}}]})
    client = MetaClient(api_key="LLM_1_test", transport=httpx.MockTransport(handler))
    out = client.ocr(image=b"\x89PNG...", timeout=30)
    assert out == "аренда 30000 сом"


def test_extract_request_model_defaults():
    r = ExtractRequest(raw_text="аренда 30000 сом")
    assert r.model == EXTRACT_MODEL
