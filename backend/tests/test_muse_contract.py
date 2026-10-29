import pytest

from backend.adapters.muse_adapter import (
    ManualInputRequired,
    MuseAdapter,
)


class FakeClient:
    def __init__(self, script):
        self.script = list(script)
        self.calls = []

    def complete(self, *, prompt: str, source_text: str, timeout: int):
        self.calls.append({"prompt": prompt, "source_text": source_text, "timeout": timeout})
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


VALID_EXTRACT = {
    "conditions": [
        {
            "term": "rent_amount",
            "value": 30000,
            "currency": "KGS",
            "quote": "аренда 30000 сом",
            "confidence": 0.9,
            "hedged": False,
        },
        {"term": "pets", "value": None, "currency": None, "quote": None, "confidence": 1.0, "hedged": False},
    ]
}


def test_extract_contract_validates_quote_and_confidence():
    client = FakeClient([VALID_EXTRACT])
    adapter = MuseAdapter(client=client)
    out = adapter.extract("аренда 30000 сом, про животных ни слова")
    by_term = {c.term: c for c in out}
    assert by_term["rent_amount"].value == 30000
    assert by_term["rent_amount"].needs_manual_check is False
    assert by_term["pets"].value is None
    assert client.calls[0]["timeout"] == 30


def test_extract_retries_once_on_invalid_json():
    client = FakeClient([{"bogus": True}, VALID_EXTRACT])
    adapter = MuseAdapter(client=client)
    out = adapter.extract("аренда 30000 сом")
    assert len(client.calls) == 2
    assert "строже" in client.calls[1]["prompt"].lower() or "strict" in client.calls[1]["prompt"].lower()
    assert {c.term for c in out} == {"rent_amount", "pets"}


def test_extract_fails_to_manual_input_not_fake_success():
    client = FakeClient([{"bogus": 1}, {"also": "bad"}])
    adapter = MuseAdapter(client=client)
    with pytest.raises(ManualInputRequired):
        adapter.extract("аренда 30000 сом")


def test_extract_rejects_quote_not_in_source():
    bad = {"conditions": [{"term": "rent_amount", "value": 99999, "currency": "KGS",
                           "quote": "аренда 99999 сом", "confidence": 0.9, "hedged": False}]}
    client = FakeClient([bad, bad])
    adapter = MuseAdapter(client=client)
    with pytest.raises(ManualInputRequired):
        adapter.extract("аренда 30000 сом")


def test_extract_coerces_bool_pets_to_yes_no():
    payload = {"conditions": [
        {"term": "pets", "value": True, "currency": None,
         "quote": "можно с котом", "confidence": 0.9, "hedged": False},
        {"term": "rent_amount", "value": 30000, "currency": "KGS",
         "quote": "аренда 30000 сом", "confidence": 0.9, "hedged": False},
    ]}
    out = MuseAdapter(client=FakeClient([payload])).extract("аренда 30000 сом, можно с котом")
    assert {c.term: c for c in out}["pets"].value == "yes"


def test_extract_rejects_pets_garbage_value():
    bad = {"conditions": [{"term": "pets", "value": 12345, "currency": None,
                           "quote": "можно с котом", "confidence": 0.9, "hedged": False}]}
    with pytest.raises(ManualInputRequired):
        MuseAdapter(client=FakeClient([bad, bad])).extract("можно с котом")


def test_extract_rejects_bad_confidence():
    bad = {"conditions": [{"term": "rent_amount", "value": 30000, "currency": "KGS",
                           "quote": "аренда 30000 сом", "confidence": 1.5, "hedged": False}]}
    client = FakeClient([bad, bad])
    adapter = MuseAdapter(client=client)
    with pytest.raises(ManualInputRequired):
        adapter.extract("аренда 30000 сом")


def test_low_confidence_sets_manual_check_by_code():
    payload = {"conditions": [{"term": "deposit", "value": 30000, "currency": "KGS",
                               "quote": "залог 30000", "confidence": 0.5, "hedged": False}]}
    client = FakeClient([payload])
    adapter = MuseAdapter(client=client)
    out = adapter.extract("залог 30000")
    assert out[0].needs_manual_check is True


def test_draft_questions_only_conflict_unknown():
    registry = [
        {"term": "rent_amount", "status": "match"},
        {"term": "deposit", "status": "conflict"},
        {"term": "pets", "status": "unknown"},
        {"term": "term", "status": "single"},
    ]
    qs = MuseAdapter(client=FakeClient([])).draft_questions(registry)
    terms = [q["term"] for q in qs]
    assert "deposit" in terms and "pets" in terms
    assert "rent_amount" not in terms and "term" not in terms


def test_owner_message_requires_manual_confirm_flag():
    msg = MuseAdapter(client=FakeClient([])).draft_owner_message([{"term": "deposit", "question": "Какой залог?"}])
    assert msg["needs_manual_confirm"] is True
    assert "Какой залог?" in msg["text"]


def test_real_api_live_only_with_key():
    import os
    if not os.environ.get("MODEL_API_KEY"):
        pytest.skip("нет MODEL_API_KEY — живой вызов запрещён, см. docs/muse-contract.md")
    from backend.adapters.meta_transport import MetaClient
    client = MetaClient(api_key=os.environ["MODEL_API_KEY"])
    out = client.complete(prompt="Верни {}", source_text="аренда 30000 сом", timeout=30)
    assert "conditions" in out
