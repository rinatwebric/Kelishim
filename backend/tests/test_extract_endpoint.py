from fastapi.testclient import TestClient

from backend.adapters.muse_adapter import MuseAdapter
from backend.app import create_app
from backend.store import DealStore


class FakeClient:
    def complete(self, *, prompt, source_text, timeout):
        assert timeout == 30
        return {"conditions": [{"term": "rent_amount", "value": 30000,
                                "currency": "KGS", "quote": source_text,
                                "confidence": 0.9, "hedged": False}]}


def _client(tmp_path, adapter=None):
    app = create_app(DealStore(str(tmp_path / "d.json")))
    app.state.extract_client = adapter
    return TestClient(app)


def test_extract_endpoint_uses_adapter(tmp_path):
    c = _client(tmp_path, MuseAdapter(client=FakeClient()))
    r = c.post("/extract", json={"raw_text": "аренда 30000 сом"})
    assert r.status_code == 200, r.text
    conds = r.json()["conditions"]
    assert conds[0]["term"] == "rent_amount"
    assert conds[0]["value"] == 30000


def test_extract_endpoint_without_key_returns_503_manual(tmp_path, monkeypatch):
    monkeypatch.setattr("backend.app.get_default_client", lambda: None)
    c = _client(tmp_path, None)
    r = c.post("/extract", json={"raw_text": "аренда 30000 сом"})
    assert r.status_code == 503
    assert "вручную" in r.json()["detail"]


def test_extract_endpoint_lazy_default_uses_env_client(tmp_path, monkeypatch):
    import backend.app as appmod
    monkeypatch.setattr(appmod, "get_default_client", lambda: FakeClient())
    app = create_app(DealStore(str(tmp_path / "d.json")))
    c = TestClient(app)
    r = c.post("/extract", json={"raw_text": "аренда 30000 сом"})
    assert r.status_code == 200, r.text
    assert r.json()["conditions"][0]["value"] == 30000
