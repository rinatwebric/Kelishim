from dataclasses import dataclass
from typing import Any, Optional

TERMS = (
    "rent_amount",
    "deposit",
    "term",
    "utilities",
    "pets",
    "prepayment",
    "repairs",
    "owner_access",
    "termination",
    "deposit_return",
)


@dataclass
class ExtractedCondition:
    term: str
    value: Optional[Any]
    currency: Optional[str] = None
    quote: Optional[str] = None
    confidence: float = 1.0
    hedged: bool = False
    needs_manual_check: bool = False
    raw_text: str = ""

    def __post_init__(self):
        if self.term not in TERMS:
            raise ValueError(f"unknown term: {self.term}")
        if self.currency is not None:
            cur = str(self.currency).strip().upper()
            if cur not in ("KGS", "USD"):
                raise ValueError(f"bad currency for {self.term}: {self.currency!r} (KGS|USD|null)")
            self.currency = cur
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0,1]")
        if self.value is None:
            return
        if not self.quote or self.quote not in self.raw_text:
            raise ValueError(f"quote must be found in raw_text for term {self.term}")
        if self.confidence < 0.6 or self.hedged:
            self.needs_manual_check = True
