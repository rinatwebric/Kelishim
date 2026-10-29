from fastapi.testclient import TestClient

from backend.app import create_app
from backend.store import DealStore


class FakeMediaClient:
    def complete(self, *, prompt, source_text, timeout):
        raise AssertionError("not used here")

    def transcribe(self, *, audio, timeout):
        assert timeout == 30
        assert audio[:4] == b"RIFF"
        return "аренда 30000 сом"

    def ocr(self, *, image, timeout):
        assert timeout == 30
        assert image[:4] == b"\x89PNG"
        return "залог 30000"


def _client(tmp_path, adapter):
    from backend.adapters.muse_adapter import MuseAdapter
    app = create_app(DealStore(str(tmp_path / "d.json")))
    app.state.extract_client = adapter if adapter is None else MuseAdapter(client=adapter)
    return TestClient(app)


def test_transcribe_returns_text(tmp_path):
    c = _client(tmp_path, FakeMediaClient())
    r = c.post("/transcribe", files={"audio": ("a.wav", b"RIFF....WAVE", "audio/wav")})
    assert r.status_code == 200, r.text
    assert r.json()["text"] == "аренда 30000 сом"


def test_ocr_returns_text(tmp_path):
    c = _client(tmp_path, FakeMediaClient())
    r = c.post("/ocr", files={"image": ("p.png", b"\x89PNG....", "image/png")})
    assert r.status_code == 200, r.text
    assert r.json()["text"] == "залог 30000"


def test_transcribe_without_file_is_422(tmp_path):
    c = _client(tmp_path, FakeMediaClient())
    assert c.post("/transcribe").status_code == 422


def test_media_without_key_returns_503_manual(tmp_path, monkeypatch):
    monkeypatch.setattr("backend.app.get_default_client", lambda: None)
    c = _client(tmp_path, None)
    r = c.post("/transcribe", files={"audio": ("a.wav", b"RIFF....", "audio/wav")})
    assert r.status_code == 503
    assert "вручную" in r.json()["detail"]
    r = c.post("/ocr", files={"image": ("p.png", b"\x89PNG....", "image/png")})
    assert r.status_code == 503


def test_transcribe_oversize_rejected(tmp_path):
    c = _client(tmp_path, FakeMediaClient())
    big = b"RIFF" + b"\x00" * (33 * 1024 * 1024)
    r = c.post("/transcribe", files={"audio": ("big.wav", big, "audio/wav")})
    assert r.status_code == 413
