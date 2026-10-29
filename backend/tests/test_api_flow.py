from fastapi.testclient import TestClient

from backend.app import create_app
from backend.store import DealStore


def _client(tmp_path):
    store = DealStore(str(tmp_path / "deals.json"))
    return TestClient(create_app(store))


def test_two_sources_plus_owner_reply_recomputes_registry(tmp_path):
    c = _client(tmp_path)
    deal = c.post("/deals").json()
    did = deal["id"]

    s1 = c.post(f"/deals/{did}/sources", json={
        "kind": "text",
        "raw_text": "аренда 30000 сом",
        "conditions": [{"term": "rent_amount", "value": 30000, "currency": "KGS",
                        "quote": "аренда 30000 сом", "confidence": 0.9, "hedged": False}],
    })
    assert s1.status_code == 200

    s2 = c.post(f"/deals/{did}/sources", json={
        "kind": "text",
        "raw_text": "аренда 35000 сом",
        "conditions": [{"term": "rent_amount", "value": 35000, "currency": "KGS",
                        "quote": "аренда 35000 сом", "confidence": 0.9, "hedged": False}],
    })
    assert s2.status_code == 200

    reg = c.get(f"/deals/{did}/registry").json()
    row = next(r for r in reg["rows"] if r["term"] == "rent_amount")
    assert row["status"] == "conflict"

    reply = c.post(f"/deals/{did}/owner_reply", json={
        "raw_text": "итого аренда 30000 сом",
        "conditions": [{"term": "rent_amount", "value": 30000, "currency": "KGS",
                        "quote": "аренда 30000 сом", "confidence": 0.95, "hedged": False}],
    })
    assert reply.status_code == 200

    reg2 = c.get(f"/deals/{did}/registry").json()
    row2 = next(r for r in reg2["rows"] if r["term"] == "rent_amount")
    # Ruling: при голосах [30000, 35000, 30000] два совпали И два различаются —
    # приоритет у conflict, противоречие нельзя прятать. Пересчёт доказан ростом entries.
    assert row2["status"] == "conflict"
    assert len(row2["entries"]) == 3


def test_deal_survives_restart_and_deletes(tmp_path):
    c = _client(tmp_path)
    did = c.post("/deals").json()["id"]
    c.post(f"/deals/{did}/sources", json={"kind": "text", "raw_text": "год",
        "conditions": [{"term": "term", "value": "год", "quote": "год", "confidence": 1.0, "hedged": False}]})
    # новый инстанс на том же файле = рестарт
    c2 = _client(tmp_path)
    reg = c2.get(f"/deals/{did}/registry").json()
    assert any(r["term"] == "term" for r in reg["rows"])
    assert c2.delete(f"/deals/{did}").status_code == 200
    assert c2.get(f"/deals/{did}/registry").status_code == 404
