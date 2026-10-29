import json

from fastapi.testclient import TestClient

from backend.app import create_app
from backend.store import DealStore


def _client(tmp_path):
    return TestClient(create_app(DealStore(str(tmp_path / "deals.json"))))


def test_preflight_allows_frontend_origin(tmp_path):
    c = _client(tmp_path)
    r = c.options("/deals", headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    })
    assert r.status_code == 200, r.text
    assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_actual_response_has_cors_header(tmp_path):
    c = _client(tmp_path)
    r = c.post("/deals", headers={"Origin": "http://localhost:5173"})
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_corrupt_json_backed_up_not_silently_wiped(tmp_path):
    p = tmp_path / "deals.json"
    p.write_text("{ не json", encoding="utf-8")
    store = DealStore(str(p))
    did = store.create_deal()
    backup = str(p) + ".corrupt"
    import os
    assert os.path.exists(backup), "битый файл должен сохраняться в .corrupt"
    assert store.get_registry(did)["rows"]
