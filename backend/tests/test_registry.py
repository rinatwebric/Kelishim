import pytest

from backend.domain.normalize import normalize_amount
from backend.domain.registry import compute_status
from backend.domain.schema import ExtractedCondition


def test_status_unknown():
    assert compute_status([None, None]) == "unknown"


def test_status_single():
    assert compute_status(["30 000 сом", None]) == "single"


def test_status_hedged_forces_single():
    assert compute_status(["30000", "30000"], [False, True]) == "single"


def test_status_match_normalized_amounts():
    a = normalize_amount("30 тыс")
    b = normalize_amount("30 000")
    assert compute_status([a, b]) == "match"


def test_status_conflict_currencies():
    a = normalize_amount("30 000 сом")
    b = normalize_amount("500 USD")
    assert a != b
    assert compute_status([a, b]) == "conflict"


def test_status_match_text_variants():
    assert compute_status(["Можно с котом", "можно с котом "]) == "match"


def test_quote_must_be_in_raw_text():
    with pytest.raises(ValueError):
        ExtractedCondition(term="rent_amount", value=30000, quote="30 000", raw_text="аренда 25 000")


def test_low_confidence_needs_manual_check():
    c = ExtractedCondition(
        term="deposit", value=30000, quote="залог 30000",
        raw_text="залог 30000", confidence=0.5,
    )
    assert c.needs_manual_check is True


def test_hedged_needs_manual_check():
    c = ExtractedCondition(
        term="pets", value="yes", quote="наверное можно",
        raw_text="наверное можно с котом", confidence=0.9, hedged=True,
    )
    assert c.needs_manual_check is True


def test_null_value_ok_without_quote():
    c = ExtractedCondition(term="pets", value=None, raw_text="про животных ни слова")
    assert c.value is None


def test_owner_reply_changes_status(tmp_path=None):
    # Ответ хозяина, подтверждающий единственный источник: single -> match.
    # Пересчёт кодом через реальный DealStore, а не подменой списка.
    import tempfile, os
    from backend.store import DealStore
    d = tempfile.mkdtemp()
    store = DealStore(os.path.join(d, "t.json"))
    did = store.create_deal()
    store.add_source(did, "text", "аренда 30000 сом", [
        {"term": "rent_amount", "value": 30000, "currency": "KGS",
         "quote": "аренда 30000 сом", "confidence": 0.9, "hedged": False}])
    before = store.get_registry(did)
    row_before = next(r for r in before["rows"] if r["term"] == "rent_amount")
    assert row_before["status"] == "single"
    store.add_source(did, "owner_reply", "да, аренда 30000 сом", [
        {"term": "rent_amount", "value": 30000, "currency": "KGS",
         "quote": "аренда 30000 сом", "confidence": 0.95, "hedged": False}])
    after = store.get_registry(did)
    row_after = next(r for r in after["rows"] if r["term"] == "rent_amount")
    assert row_after["status"] == "match"
    assert len(row_after["entries"]) == 2


def test_currency_case_insensitive():
    from backend.domain.schema import ExtractedCondition
    c = ExtractedCondition(term="rent_amount", value=30000, currency="kgs",
                           quote="аренда 30000", raw_text="аренда 30000")
    assert c.currency == "KGS"
