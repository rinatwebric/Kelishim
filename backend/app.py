from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.store import DealStore


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


def create_app(store: DealStore | None = None) -> FastAPI:
    app = FastAPI(title="Kelishim")
    app.state.store = store or DealStore()

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

    return app


app = create_app()
