"""Честный прогон eval-образцов через compute_status (доменное ядро, без модели)."""
import json
import glob
import os

from backend.domain.registry import compute_status

ok_count, total = 0, 0
lines = ["| sample | эталон | получено | итог |", "|---|---|---|---|"]
for path in sorted(glob.glob(os.path.join(os.path.dirname(__file__), "fixtures", "*.json"))):
    fix = json.load(open(path, encoding="utf-8"))
    got = {}
    for term, spec in fix["terms"].items():
        vals = [tuple(v) if isinstance(v, list) else v for v in spec["values"]]
        got[term] = compute_status(vals, spec.get("hedged") or None)
    ok = all(got.get(k) == v for k, v in fix["expected"].items())
    total += 1
    ok_count += ok
    lines.append(f"| {fix['id']} | {fix['expected']} | {got} | {'ВЕРНО' if ok else 'ОШИБКА'} |")
lines.append(f"\nИтого: {ok_count}/{total} образцов сошлись.")
print("\n".join(lines))
