from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.adapters.muse_adapter import ManualInputRequired
from backend.store import DealStore

FRONTEND_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


class ConditionIn(BaseModel):
    term: str
    value: Optional[Any] = None
    currency: Optional[str] = None
    quote: Optional[str] = None
    confidence: float = 1.0
    hedged: bool = False


class SourceIn(BaseModel):
    kind: str = "text"
    raw_text: str
    conditions: list[ConditionIn] = []


class RawTextIn(BaseModel):
    raw_text: str


def create_app(store: DealStore | None = None, extract_client=None) -> FastAPI:
    app = FastAPI(title="Kelishim")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=FRONTEND_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.store = store or DealStore()
    app.state.extract_client = extract_client

    @app.post("/deals")
    def post_deal():
        return {"id": app.state.store.create_deal()}

    def _add(deal_id: str, kind: str, src: SourceIn):
        try:
            return app.state.store.add_source(
                deal_id, kind, src.raw_text, [c.model_dump() for c in src.conditions]
            )
        except KeyError:
            raise HTTPException(404, "deal not found")
        except ValueError as e:
            raise HTTPException(422, str(e))

    @app.post("/deals/{deal_id}/sources")
    def post_source(deal_id: str, src: SourceIn):
        return _add(deal_id, src.kind or "text", src)

    @app.post("/deals/{deal_id}/owner_reply")
    def post_reply(deal_id: str, src: SourceIn):
        return _add(deal_id, "owner_reply", src)

    @app.get("/deals/{deal_id}/registry")
    def get_registry(deal_id: str):
        try:
            return app.state.store.get_registry(deal_id)
        except KeyError:
            raise HTTPException(404, "deal not found")

    @app.delete("/deals/{deal_id}")
    def delete_deal(deal_id: str):
        try:
            app.state.store.delete_deal(deal_id)
            return {"ok": True}
        except KeyError:
            raise HTTPException(404, "deal not found")

    @app.post("/extract")
    def post_extract(body: RawTextIn):
        from backend.adapters.muse_adapter import MuseAdapter

        client = app.state.extract_client
        if client is None:
            raise HTTPException(
                503,
                "Извлечение недоступно: нет MODEL_API_KEY. Введите условия вручную — исходник сохранён.",
            )
        adapter = client if isinstance(client, MuseAdapter) else MuseAdapter(client=client)
        try:
            conds = adapter.extract(body.raw_text)
        except ManualInputRequired as e:
            raise HTTPException(503, str(e))
        return {"conditions": [
            {"term": c.term, "value": c.value, "currency": c.currency,
             "quote": c.quote, "confidence": c.confidence, "hedged": c.hedged,
             "needs_manual_check": c.needs_manual_check}
            for c in conds]}

    return app


app = create_app()
