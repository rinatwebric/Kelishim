import re
from typing import Optional, Tuple

_KGS = ("сом", "сомов", "kgs", "сўм")
_USD = ("usd", "$", "долл")


def _detect_currency(s: str) -> Optional[str]:
    low = s.lower()
    if any(k in low for k in _USD):
        return "USD"
    if any(k in low for k in _KGS):
        return "KGS"
    return None


def normalize_amount(raw: str) -> Tuple[Optional[int], Optional[str]]:
    if not raw or not raw.strip():
        return (None, None)
    s = raw.strip().lower().replace("\u00a0", " ")
    if any(p in s for p in ("договор", "не указан", "неизвестно", "n/a")):
        return (None, None)
    currency = _detect_currency(s)
    t = s
    for k in ("сомов", "сом", "kgs", "usd", "$", "долларов", "доллары", "доллара", "доллар"):
        t = t.replace(k, " ")
    t = t.strip()
    mult = 1
    if "тыс" in t or "тысяч" in t:
        mult = 1000
        t = t.replace("тысяч", " ").replace("тыс", " ")
    else:
        m_k = re.search(r"(\d[\d\s.,]*)\s*[кk]\b", t)
        if m_k:
            mult = 1000
            t = t[: m_k.start()] + " " + m_k.group(1) + " " + t[m_k.end():]
    m = re.search(r"\d[\d\s.,]*", t)
    if not m:
        return (None, None)
    num = m.group(0).replace(" ", "").replace(",", ".")
    try:
        val = float(num) * mult
    except ValueError:
        return (None, None)
    return (int(val), currency)


def normalize_term(raw: str) -> Optional[int]:
    if not raw or not raw.strip():
        return None
    s = raw.strip().lower()
    if "полгода" in s:
        return 6
    m = re.search(r"(\d+)\s*(мес|месяц)", s)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s*(год|года|лет|г\.)", s)
    if m:
        return int(m.group(1)) * 12
    if s.strip() in ("год", "на год", "1 год"):
        return 12
    return None


def normalize_pets(raw: str) -> str:
    if not raw or not raw.strip():
        return "unknown"
    s = raw.strip().lower()
    if "договор" in s:
        return "negotiable"
    if any(k in s for k in ("без животн", "нельзя", "запрещ")) or re.search(r"\bнет\b", s):
        return "no"
    if any(k in s for k in ("можно", "разреш", "с котом", "с собакой")) or re.search(r"\bда\b", s):
        return "yes"
    return "unknown"
