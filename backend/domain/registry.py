from typing import Any, List

Status = str  # unknown | single | match | conflict


def _norm_key(v: Any) -> Any:
    if isinstance(v, str):
        return v.strip().lower()
    if isinstance(v, (list, tuple)):
        return tuple(_norm_key(x) for x in v)
    return v


def _is_missing(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, tuple) and len(v) == 2 and v[0] is None and v[1] is None:
        return True
    return False


def _amounts_equal(a: Any, b: Any) -> bool:
    if isinstance(a, tuple) and isinstance(b, tuple) and len(a) == 2 and len(b) == 2:
        n1, c1 = a
        n2, c2 = b
        if n1 != n2:
            return False
        if c1 is not None and c2 is not None and c1 != c2:
            return False
        return True
    return _norm_key(a) == _norm_key(b)


def compute_status(values: List[Any], hedged_flags: List[bool] | None = None) -> Status:
    present = [v for v in values if not _is_missing(v)]
    if not present:
        return "unknown"
    if len(present) == 1:
        return "single"
    if hedged_flags and any(hedged_flags):
        return "single"
    first = present[0]
    if all(_amounts_equal(first, v) for v in present[1:]):
        return "match"
    return "conflict"
