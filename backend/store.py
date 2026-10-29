from __future__ import annotations

import json
import os
import uuid

from backend.domain.normalize import normalize_amount, normalize_pets, normalize_term
from backend.domain.registry import compute_status
from backend.domain.schema import TERMS, ExtractedCondition

MONEY_TERMS = ("rent_amount", "deposit", "prepayment")


def _comparable(term: str, value, currency):
    if value is None:
        return None
    if term in MONEY_TERMS:
        if isinstance(value, (int, float)):
            return (int(value), currency)
        n, c = normalize_amount(f"{value} {currency or ''}")
        return (n, c or currency) if n is not None else value
    if term == "term":
        return normalize_term(str(value)) if not isinstance(value, int) else value
    if term == "pets":
        return normalize_pets(str(value)) if value not in ("yes", "no", "negotiable", "unknown") else value
    return value


class DealStore:
    def __init__(self, path: str | None = None):
        self.path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "deals.json")
        self._deals: dict = {}
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, encoding="utf-8") as f:
                    self._deals = json.load(f).get("deals", {})
            except OSError:
                self._deals = {}
            except json.JSONDecodeError:
                backup = self.path + ".corrupt"
                try:
                    os.replace(self.path, backup)
                except OSError:
                    pass
                self._deals = {}

    def _save(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"deals": self._deals}, f, ensure_ascii=False)

    def create_deal(self) -> str:
        did = uuid.uuid4().hex[:8]
        self._deals[did] = {"id": did, "sources": []}
        self._save()
        return did

    def add_source(self, deal_id: str, kind: str, raw_text: str, conditions: list[dict]) -> dict:
        if deal_id not in self._deals:
            raise KeyError(deal_id)
        checked = []
        for c in conditions:
            ec = ExtractedCondition(
                term=c["term"], value=c.get("value"), currency=c.get("currency"),
                quote=c.get("quote"), confidence=float(c.get("confidence", 1.0)),
                hedged=bool(c.get("hedged", False)), raw_text=raw_text,
            )
            checked.append({
                "term": ec.term, "value": ec.value, "currency": ec.currency,
                "quote": ec.quote, "confidence": ec.confidence,
                "hedged": ec.hedged, "needs_manual_check": ec.needs_manual_check,
            })
        src = {"kind": kind, "raw_text": raw_text, "conditions": checked}
        self._deals[deal_id]["sources"].append(src)
        self._save()
        return src

    def delete_deal(self, deal_id: str):
        if deal_id not in self._deals:
            raise KeyError(deal_id)
        del self._deals[deal_id]
        self._save()

    def get_registry(self, deal_id: str) -> dict:
        if deal_id not in self._deals:
            raise KeyError(deal_id)
        rows = []
        sources = self._deals[deal_id]["sources"]
        for term in TERMS:
            entries = [c for s in sources for c in s["conditions"] if c["term"] == term]
            comparables = [_comparable(term, e["value"], e.get("currency")) for e in entries]
            hedged = [bool(e["hedged"]) for e in entries]
            status = compute_status(comparables, hedged) if entries else "unknown"
            rows.append({
                "term": term,
                "status": status,
                "entries": entries,
                "needs_manual_check": any(e["needs_manual_check"] for e in entries),
            })
        return {"id": deal_id, "rows": rows}
