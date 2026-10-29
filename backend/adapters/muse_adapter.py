from __future__ import annotations

from typing import Any, Protocol

from backend.domain.schema import TERMS, ExtractedCondition

TIMEOUT = 30
MAX_RETRIES = 1

BASE_EXTRACT_PROMPT = (
    "Верни ТОЛЬКО JSON по схеме {\"conditions\": ["
    "{\"term\": <один из 10>, \"value\": <значение|null>, \"currency\": <KGS|USD|null>, "
    "\"quote\": <точная цитата|null>, \"confidence\": <0..1>, \"hedged\": <bool>}]}. "
    "Термы: " + ", ".join(TERMS) + ". "
    "Отсутствует — value null. Цитата обязана дословно быть в исходнике."
)
STRICT_SUFFIX = (
    " Ответь строже / strict: только валидный JSON, без прозы. "
    "Проверь: quote дословно из исходника, confidence в [0,1], термы из списка."
)


class ManualInputRequired(Exception):
    """Модель не справилась — нужен ручной ввод. Никогда не подменять фейковым успехом."""


class MuseClient(Protocol):
    def complete(self, *, prompt: str, source_text: str, timeout: int) -> Any:
        ...


class MuseAdapter:
    def __init__(self, client: MuseClient, timeout: int = TIMEOUT):
        self.client = client
        self.timeout = timeout

    def extract(self, source_text: str) -> list[ExtractedCondition]:
        attempts = [BASE_EXTRACT_PROMPT, BASE_EXTRACT_PROMPT + STRICT_SUFFIX]
        last_error: Exception | None = None
        for prompt in attempts[: MAX_RETRIES + 1]:
            try:
                payload = self.client.complete(prompt=prompt, source_text=source_text, timeout=self.timeout)
            except TimeoutError as e:
                last_error = e
                continue
            except ManualInputRequired as e:
                raise e
            except Exception as e:
                last_error = e
                continue
            try:
                return self._validate(payload, source_text)
            except ValueError as e:
                last_error = e
                continue
        raise ManualInputRequired(
            f"Не удалось распознать условия автоматически ({last_error}). "
            "Введите условия вручную — исходник сохранён."
        )

    def _validate(self, payload: Any, source_text: str) -> list[ExtractedCondition]:
        if not isinstance(payload, dict) or not isinstance(payload.get("conditions"), list):
            raise ValueError("payload must be {conditions: [...]}")
        out: list[ExtractedCondition] = []
        for item in payload["conditions"]:
            if not isinstance(item, dict):
                raise ValueError("condition must be an object")
            term = item.get("term")
            if term not in TERMS:
                raise ValueError(f"unknown term: {term}")
            conf = item.get("confidence", 1.0)
            if not isinstance(conf, (int, float)) or not 0.0 <= float(conf) <= 1.0:
                raise ValueError(f"bad confidence for {term}: {conf}")
            out.append(
                ExtractedCondition(
                    term=term,
                    value=item.get("value"),
                    currency=item.get("currency"),
                    quote=item.get("quote"),
                    confidence=float(conf),
                    hedged=bool(item.get("hedged", False)),
                    raw_text=source_text,
                )
            )
        return out

    def draft_questions(self, registry: list[dict]) -> list[dict]:
        return [
            {"term": r["term"], "question": f"Уточните: {r['term']}?"}
            for r in registry
            if r.get("status") in ("conflict", "unknown")
        ]

    def draft_owner_message(self, questions: list[dict]) -> dict:
        lines = [f"• {q.get('question', q.get('term'))}" for q in questions]
        return {
            "text": "Здравствуйте! Уточните, пожалуйста:\n" + "\n".join(lines),
            "needs_manual_confirm": True,
        }

    def transcribe(self, audio: bytes) -> str:
        fn = getattr(self.client, "transcribe", None)
        if fn is None:
            raise ManualInputRequired("Расшифровка аудио недоступна — введите текст вручную.")
        return fn(audio=audio, timeout=self.timeout)

    def ocr(self, image: bytes) -> str:
        fn = getattr(self.client, "ocr", None)
        if fn is None:
            raise ManualInputRequired("Распознавание фото недоступно — введите текст вручную.")
        return fn(image=image, timeout=self.timeout)

    def translate_kg(self, text: str) -> str:
        try:
            out = self.client.complete(
                prompt="Переведи на кыргызский, сохрани смысл. Только перевод.",
                source_text=text,
                timeout=self.timeout,
            )
        except Exception as e:
            raise ManualInputRequired(f"Перевод недоступен ({e}). Остаётся русская версия.") from e
        if isinstance(out, dict) and isinstance(out.get("text"), str):
            return out["text"]
        if isinstance(out, str):
            return out
        raise ManualInputRequired("Перевод недоступен. Остаётся русская версия.")
