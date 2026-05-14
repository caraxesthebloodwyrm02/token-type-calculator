"""Tests for the Dark Mark system: is_dark_mark_cast, check_dark_mark,
check_imperius_compromise, and the DarkMark dataclass.
"""
from calculator import TOKEN_COLORS, TOKEN_WEIGHTS, check_dark_mark, check_imperius_compromise
from design import DarkMark, Exchange, is_dark_mark_cast

# ── is_dark_mark_cast ─────────────────────────────────────────────────────────

def test_dark_mark_fires_at_full_engagement_zero_service_corrupted():
    exchange = Exchange(attention_cost=1.0, money_cost=0.0, body_cost=0.0,
                        received_function=0.0, received_relief=0.0, received_clarity=0.0)
    assert is_dark_mark_cast(exchange, "corrupted") is True


def test_dark_mark_requires_corrupted_bond():
    """With static bond_dynamics the Dark Mark must NOT fire, even at (1.0, 0.0)."""
    exchange = Exchange(attention_cost=1.0, money_cost=0.0, body_cost=0.0,
                        received_function=0.0, received_relief=0.0, received_clarity=0.0)
    assert is_dark_mark_cast(exchange, "static") is False


def test_dark_mark_requires_full_engagement():
    """Engagement below 1.0 must not trigger the Dark Mark."""
    exchange = Exchange(attention_cost=0.8, money_cost=0.0, body_cost=0.0,
                        received_function=0.0, received_relief=0.0, received_clarity=0.0)
    assert is_dark_mark_cast(exchange, "corrupted") is False


def test_dark_mark_requires_zero_service():
    """Any service returned (> 0) must prevent the Dark Mark."""
    exchange = Exchange(attention_cost=1.0, money_cost=0.0, body_cost=0.0,
                        received_function=0.0, received_relief=0.0, received_clarity=0.1)
    assert is_dark_mark_cast(exchange, "corrupted") is False


def test_dark_mark_multi_cost_reaches_threshold():
    """Engagement can be split across cost axes to reach 1.0."""
    exchange = Exchange(attention_cost=0.4, money_cost=0.3, body_cost=0.3,
                        received_function=0.0, received_relief=0.0, received_clarity=0.0)
    assert is_dark_mark_cast(exchange, "corrupted") is True


# ── check_dark_mark ───────────────────────────────────────────────────────────

def test_check_dark_mark_returns_dark_mark_object():
    exchange = Exchange(attention_cost=1.0, received_clarity=0.0)
    mark = check_dark_mark(exchange, "corrupted")
    assert mark is not None
    assert isinstance(mark, DarkMark)
    assert mark.shape == "serpent_skull"
    assert mark.engagement == 1.0
    assert mark.service == 0.0
    assert mark.is_no_take is True
    assert mark.bond_dynamics == "corrupted"


def test_check_dark_mark_returns_none_when_no_cast():
    exchange = Exchange(attention_cost=1.0, received_clarity=0.0)
    mark = check_dark_mark(exchange, "static")
    assert mark is None


# ── DarkMark dataclass ────────────────────────────────────────────────────────

def test_dark_mark_defaults():
    mark = DarkMark(shape="serpent_skull")
    assert mark.engagement == 1.0
    assert mark.service == 0.0
    assert mark.is_no_take is True
    assert mark.bond_dynamics == "corrupted"
    assert mark.source_bind == ""


def test_dark_mark_shapes():
    for shape in ["serpent_skull", "coercion_bind", "fear_anchor"]:
        mark = DarkMark(shape=shape)
        assert mark.shape == shape


# ── check_imperius_compromise ─────────────────────────────────────────────────

def test_imperius_compromise_fires_with_both_tokens():
    assert check_imperius_compromise({"imperius", "gate-on"}) is True


def test_imperius_compromise_requires_both_tokens():
    assert check_imperius_compromise({"imperius"}) is False
    assert check_imperius_compromise({"gate-on"}) is False
    assert check_imperius_compromise({"transistor", "gate-on"}) is False


def test_imperius_not_triggered_by_unrelated_tokens():
    assert check_imperius_compromise({"transistor", "bio-signal", "anomaly"}) is False


# ── Token registry ────────────────────────────────────────────────────────────

def test_dark_mark_tokens_in_weight_registry():
    for token in ("morsmordre", "legilimens", "imperius"):
        assert token in TOKEN_WEIGHTS, f"{token} missing from TOKEN_WEIGHTS"
        assert token in TOKEN_COLORS, f"{token} missing from TOKEN_COLORS"


def test_morsmordre_weight_below_transistor():
    """morsmordre is the highest dark token but clean carrier (transistor) still wins."""
    assert TOKEN_WEIGHTS["morsmordre"] < TOKEN_WEIGHTS["transistor"]
    assert TOKEN_WEIGHTS["morsmordre"] > TOKEN_WEIGHTS["gate-on"]
