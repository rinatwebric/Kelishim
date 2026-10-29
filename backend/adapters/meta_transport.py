"""Реальный транспорт Meta Model API (https://dev.meta.ai/docs).

Источники контракта (проверено 2026-10-29):
- Обзор/base URL/auth: https://dev.meta.ai/docs/overview
  base https://api.meta.ai/v1, Bearer MODEL_API_KEY (ключи вида LLM_...),
  модели muse-spark-1.3/1.2/1.1, muse-wonder-1.0.
- Structured output: https://dev.meta.ai/docs/structured-output
  Chat Completions response_format {type: json_schema, json_schema: {...}},
  декодинг ограничен схемой; ответ — JSON-строка в choices[0].message.content.
- Auth: https://dev.meta.ai/docs/authentication — ключ только сервером,
  никогда во frontend; хранить в env MODEL_API_KEY.
- ASR файл: https://dev.meta.ai/docs/speech-to-text
  POST https://api.meta.ai/v1/asr/transcribe, multipart (request JSON + audio WAV
  mono 16-bit 16/24 kHz), модель muse-voice-transcribe-1.0; доп. лимиты:
  32 MB / 10 минут; 429 → backoff; 500 → 1 retry.
- OCR через image understanding: chat completions с image_url (data URL),
  structured output из изображений документирован на structured-output.

Ключ читается только из env. Без MODEL_API_KEY транспорт не создаётся —
см. get_default_client(): endpoint отвечает 503 + ручной ввод.
"""
from __future__ import annotations

import base64
import json
import os

import httpx
from pydantic import BaseModel

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_URL = os.environ.get("MODEL_BASE_URL", "https://api.meta.ai/v1")
EXTRACT_MODEL = os.environ.get("EXTRACT_MODEL", "muse-spark-1.3")
ASR_MODEL = "muse-voice-transcribe-1.0"

TERMS = (
    "rent_amount", "deposit", "term", "utilities", "pets",
    "prepayment", "repairs", "owner_access", "termination", "deposit_return",
)


def build_extract_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "conditions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "term": {"type": "string", "enum": list(TERMS)},
                        "value": {},
                        "currency": {"type": ["string", "null"], "enum": ["KGS", "USD", None]},
                        "quote": {"type": ["string", "null"]},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "hedged": {"type": "boolean"},
                    },
                    "required": ["term", "value", "quote", "confidence", "hedged"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["conditions"],
        "additionalProperties": False,
    }


class ExtractRequest(BaseModel):
    raw_text: str
    model: str = EXTRACT_MODEL


class MetaClient:
    """httpx-транспорт. timeout прокидывается на каждый вызов (план: 30с)."""

    def __init__(self, api_key: str, base_url: str = BASE_URL,
                 transport: httpx.BaseTransport | None = None):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._http = httpx.Client(transport=transport) if transport else httpx.Client()

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def complete(self, *, prompt: str, source_text: str, timeout: int = 30) -> dict:
        body = {
            "model": EXTRACT_MODEL,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": source_text},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "KelishimExtract", "schema": build_extract_schema()},
            },
        }
        r = self._http.post(f"{self.base_url}/chat/completions",
                            headers=self._headers(), content=json.dumps(body),
                            timeout=timeout)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        return json.loads(content)

    def transcribe(self, audio: bytes, timeout: int = 30) -> str:
        request_part = json.dumps({"mode": "PUSH_TO_TALK", "model": ASR_MODEL,
                                   "audioEncoding": "WAV"})
        files = {"audio": ("audio.wav", audio, "audio/wav")}
        data = {"request": request_part}
        r = self._http.post(
            "https://api.meta.ai/v1/asr/transcribe",
            headers={"Authorization": f"Bearer {self.api_key}"},
            files=files, data=data, timeout=timeout)
        r.raise_for_status()
        return r.json()["transcript"]

    def ocr(self, image: bytes, mime: str = "image/png", timeout: int = 30) -> str:
        b64 = base64.b64encode(image).decode()
        body = {
            "model": EXTRACT_MODEL,
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": "Transcribe all visible text verbatim. Return only the text."},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            ]}],
        }
        r = self._http.post(f"{self.base_url}/chat/completions",
                            headers=self._headers(), content=json.dumps(body),
                            timeout=timeout)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


def get_default_client() -> MetaClient | None:
    key = os.environ.get("MODEL_API_KEY")
    if not key:
        return None
    return MetaClient(api_key=key)
