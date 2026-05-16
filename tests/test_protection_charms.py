"""Tests for protection charms: PROTEGO weight, freedom-signal override,
MCGONAGALL + DOBBY scenario integrity, and the compute() integration.
"""
from calculator import (
    TOKEN_COLORS,
    TOKEN_WEIGHTS,
    TokenTypeCalculator,
    check_freedom_signal,
)
from design import Exchange

# ── PROTEGO / freedom-signal token registry ───────────────────────────────────

def test_protego_in_weight_registry():
    assert "protego" in TOKEN_WEIGHTS
    assert TOKEN_WEIGHTS["protego"] == 0.75


def test_freedom_signal_in_weight_registry():
    assert "freedom-signal" in TOKEN_WEIGHTS
    assert TOKEN_WEIGHTS["freedom-signal"] == 0.82


def test_protego_and_freedom_signal_in_color_registry():
    assert "protego" in TOKEN_COLORS
    assert "freedom-signal" in TOKEN_COLORS


# ── check_freedom_signal gate function ───────────────────────────────────────

def test_freedom_signal_fires_with_token_and_engagement():
    exchange = Exchange(engagement_cost=0.9, service_value=0.0)
    assert check_freedom_signal({"freedom-signal", "transistor"}, exchange) is True


def test_freedom_signal_requires_engagement_threshold():
    """Engagement below 0.8 must NOT trigger freedom override."""
    exchange = Exchange(engagement_cost=0.5, service_value=0.0)
    assert check_freedom_signal({"freedom-signal"}, exchange) is False


def test_freedom_signal_requires_token_present():
    """Without freedom-signal token the gate must not fire."""
    exchange = Exchange(engagement_cost=1.0, service_value=0.0)
    assert check_freedom_signal({"transistor", "bio-signal"}, exchange) is False


def test_freedom_signal_engagement_exactly_at_threshold():
    """Exactly 0.8 engagement must trigger (>= not >)."""
    exchange = Exchange(engagement_cost=0.8, service_value=0.0)
    assert check_freedom_signal({"freedom-signal"}, exchange) is True


# ── compute() integration: freedom_override flag ─────────────────────────────

def test_compute_freedom_override_flips_no_take():
    """When freedom-signal is active with sufficient engagement and NO-TAKE would fire,
    the boundary must be overridden to OPEN and freedom_override must be True.
    """
    calc = TokenTypeCalculator()
    calc.active_tokens = {"transistor", "freedom-signal"}
    calc.params["engagement_cost"] = 1.0
    calc.params["service_value"] = 0.0   # would normally be NO-TAKE
    result = calc.compute()
    assert result["freedom_override"] is True
    assert result["is_no_take"] is False
    assert result["boundary_status"] == "OPEN (FREEDOM)"


def test_compute_freedom_override_false_when_not_active():
    """Normal NO-TAKE scenario must not set freedom_override."""
    calc = TokenTypeCalculator()
    calc.active_tokens = {"transistor"}
    calc.params["engagement_cost"] = 1.0
    calc.params["service_value"] = 0.0
    result = calc.compute()
    assert result["freedom_override"] is False
    assert result["is_no_take"] is True


# ── MCGONAGALL scenario consistency ──────────────────────────────────────────

def test_mcgonagall_high_clarity():
    from calculator import SCENARIO_LIBRARY
    fp = SCENARIO_LIBRARY["MCGONAGALL"]
    assert fp.clarity >= 0.85, "McGonagall's clarity should be high — her instructions are always clear"
    assert fp.is_no_take is False


def test_dobby_freedom_anchor():
    """Dobby's fingerprint is the reference anchor for FREEDOM_SIGNAL:
    moderate-high engagement paid, meaningful clarity returned, is_no_take False.
    """
    from calculator import SCENARIO_LIBRARY
    fp = SCENARIO_LIBRARY["DOBBY"]
    assert fp.pressure >= 0.7
    assert fp.clarity >= 0.5
    assert fp.is_no_take is False
    assert fp.dominant_type == "BIO_SIGNAL"
