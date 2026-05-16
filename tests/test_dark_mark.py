"""Tests for the Dark Mark system: is_dark_mark_cast, check_dark_mark,
check_imperius_compromise, and the DarkMark dataclass.

Integration coverage (compute() path):
- Full trigger: imperius + gate-on + (1.0, 0.0) → dark_mark_state populated
- Bond guard: no imperius → bond stays static → dark_mark_state is None
- Compromise requires gate-on: imperius alone → no compromise → dark_mark_state is None
- gate_color is TOKEN_COLORS["imperius"] when COMPROMISED
"""
from calculator import TOKEN_COLORS, TOKEN_WEIGHTS, TokenTypeCalculator, check_dark_mark, check_imperius_compromise
from design import DarkMark, Exchange, is_dark_mark_cast

# ── is_dark_mark_cast ─────────────────────────────────────────────────────────

def test_dark_mark_fires_at_full_engagement_zero_service_corrupted():
    exchange = Exchange(engagement_cost=1.0, service_value=0.0)
    assert is_dark_mark_cast(exchange, "corrupted") is True


def test_dark_mark_requires_corrupted_bond():
    """With static bond_dynamics the Dark Mark must NOT fire, even at (1.0, 0.0)."""
    exchange = Exchange(engagement_cost=1.0, service_value=0.0)
    assert is_dark_mark_cast(exchange, "static") is False


def test_dark_mark_requires_full_engagement():
    """Engagement below 1.0 must not trigger the Dark Mark."""
    exchange = Exchange(engagement_cost=0.8, service_value=0.0)
    assert is_dark_mark_cast(exchange, "corrupted") is False


def test_dark_mark_requires_zero_service():
    """Any service returned (> 0) must prevent the Dark Mark."""
    exchange = Exchange(engagement_cost=1.0, service_value=0.1)
    assert is_dark_mark_cast(exchange, "corrupted") is False


# ── check_dark_mark ───────────────────────────────────────────────────────────

def test_check_dark_mark_returns_dark_mark_object():
    exchange = Exchange(engagement_cost=1.0, service_value=0.0)
    mark = check_dark_mark(exchange, "corrupted")
    assert mark is not None
    assert isinstance(mark, DarkMark)
    assert mark.shape == "serpent_skull"
    assert mark.engagement == 1.0
    assert mark.service == 0.0
    assert mark.is_no_take is True
    assert mark.bond_dynamics == "corrupted"


def test_check_dark_mark_returns_none_when_no_cast():
    exchange = Exchange(engagement_cost=1.0, service_value=0.0)
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


# ── compute() integration — full Dark Mark path ───────────────────────────────

def _calc_at(tokens: set, engagement: float, service: float) -> dict:
    calc = TokenTypeCalculator()
    calc.active_tokens = tokens
    calc.params["engagement_cost"] = engagement
    calc.params["service_value"] = service
    return calc.compute()


def test_compute_dark_mark_fires_with_imperius_gate_on_full_take():
    """imperius + gate-on + (1.0, 0.0) is the only path that sets bond_dynamics=corrupted
    inside compute(), so dark_mark_state must be non-None with all correct fields.
    """
    result = _calc_at({"transistor", "gate-on", "imperius"}, 1.0, 0.0)
    dms = result["dark_mark_state"]
    assert dms is not None
    assert dms["shape"] == "serpent_skull"
    assert dms["engagement"] == 1.0
    assert dms["service"] == 0.0
    assert dms["is_no_take"] is True
    assert dms["bond_dynamics"] == "corrupted"


def test_compute_dark_mark_none_without_imperius():
    """Without imperius, compute() keeps bond_dynamics='static' even at (1.0, 0.0).
    Dark Mark must not fire — the static bond is the guard.
    """
    result = _calc_at({"transistor", "gate-on"}, 1.0, 0.0)
    assert result["dark_mark_state"] is None


def test_compute_dark_mark_none_when_imperius_without_gate_on():
    """imperius alone does not trigger check_imperius_compromise (gate-on is required),
    so bond_dynamics stays 'static' and dark_mark_state must be None.
    """
    result = _calc_at({"transistor", "imperius"}, 1.0, 0.0)
    assert result["gate_state"] != "COMPROMISED"
    assert result["dark_mark_state"] is None


def test_compute_dark_mark_none_when_service_returned():
    """Even with imperius + gate-on, any service_value > 0 prevents the Dark Mark."""
    result = _calc_at({"transistor", "gate-on", "imperius"}, 1.0, 0.5)
    assert result["dark_mark_state"] is None


def test_compute_gate_color_is_imperius_color_when_compromised():
    """gate_color must be TOKEN_COLORS['imperius'] when the gate state is COMPROMISED."""
    result = _calc_at({"transistor", "gate-on", "imperius"}, 0.5, 0.5)
    assert result["gate_state"] == "COMPROMISED"
    assert result["gate_color"] == TOKEN_COLORS["imperius"]
