from backend.domain.normalize import normalize_amount, normalize_term, normalize_pets


def test_amount_variants():
    assert normalize_amount("30 тыс") == (30000, None)
    assert normalize_amount("30 000") == (30000, None)
    assert normalize_amount("30к") == (30000, None)
    assert normalize_amount("30000 сом") == (30000, "KGS")
    assert normalize_amount("500 USD") == (500, "USD")


def test_amount_none():
    assert normalize_amount("") == (None, None)
    assert normalize_amount("по договорённости") == (None, None)


def test_currency_not_mixed():
    v1 = normalize_amount("30 000 сом")
    v2 = normalize_amount("500 USD")
    assert v1[1] != v2[1]


def test_term_months():
    assert normalize_term("год") == 12
    assert normalize_term("6 месяцев") == 6
    assert normalize_term("") is None


def test_pets():
    assert normalize_pets("можно с котом") == "yes"
    assert normalize_pets("без животных") == "no"
    assert normalize_pets("по договорённости") == "negotiable"
    assert normalize_pets("") == "unknown"
