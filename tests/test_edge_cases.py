"""Edge case tests: Patronus + DarkMark coordinate exclusion, SIRIUS transition
similarity, token arithmetic with new tokens, imperius gate state integration.
"""
import pytest
from design import Exchange, BondMemory, is_dark_mark_cast
from calculator import (
    TokenTypeCalculator, SCENARIO_LIBRARY, TOKEN_WEIGHTS,
    expecto_patronum, check_dark_mark, check_imperius_compromise,
)


# ── Patronus / DarkMark coordinate exclusion ──────────────────────────────────

def test_patronus_and_dark_mark_cannot_coexist():
    """Patronus fires at (engagement=1.0, service=1.0, bond=static).
    Dark Mark fires at (engagement=1.0, service=0.0, bond=corrupted).
    The same exchange cannot satisfy both conditions simultaneously.
    """
    full_service_exchange = Exchange(
        attention_cost=1.0,
        received_clarity=1.0
    )
    full_take_exchange = Exchange(
        attention_cost=1.0,
        received_clarity=0.0
    )
    anchor = BondMemory(content="anchor", bond_dynamics="static")

    patronus = expecto_patronum(full_service_exchange, anchor)
    dark_mark = check_dark_mark(full_take_exchange, "corrupted")

    assert patronus is not None   # full service → Patronus fires
    assert dark_mark is not None  # zero service + corrupted → Dark Mark fires

    # They cannot fire from the same exchange
    patronus_from_no_take = expecto_patronum(full_take_exchange, anchor)
    dark_mark_from_full = check_dark_mark(full_service_exchange, "corrupted")

    assert patronus_from_no_take is None  # service=0 → Patronus cannot fire
    assert dark_mark_from_full is None    # service>0 → Dark Mark cannot fire


def test_voldemort_fingerprint_is_opposite_of_lily():
    """LILY (1.0, 1.0) and VOLDEMORT (1.0, 0.0) share maximum pressure but
    are opposite on clarity — the defining axis of the Dark vs Light split.
    """
    voldemort = SCENARIO_LIBRARY["VOLDEMORT"]
    lily = SCENARIO_LIBRARY["LILY"]
    assert voldemort.pressure == lily.pressure == 1.0
    assert voldemort.clarity == 0.0
    assert lily.clarity == 1.0
    assert voldemort.is_no_take is True
    assert lily.is_no_take is False


# ── SIRIUS transition similarity ──────────────────────────────────────────────

def test_sirius_black_and_padfoot_similarity():
    """SIRIUS_BLACK and PADFOOT should be similar (same character, adjacent states)
    but not identical — the transition from imprisoned to active shifts clarity.
    """
    calc = TokenTypeCalculator()
    sirius = SCENARIO_LIBRARY["SIRIUS_BLACK"]
    padfoot = SCENARIO_LIBRARY["PADFOOT"]
    report = calc.calculate_similarity(sirius, padfoot)
    # They should be meaningfully similar but not an exact match
    assert report.similarity > 0.4, "SIRIUS_BLACK and PADFOOT should have meaningful similarity"
    assert report.similarity < 1.0, "They are not identical entries"


def test_sirius_black_not_match_with_voldemort():
    """SIRIUS_BLACK (protector, is_no_take=False) must not be a close match to VOLDEMORT."""
    calc = TokenTypeCalculator()
    sirius = SCENARIO_LIBRARY["SIRIUS_BLACK"]
    voldemort = SCENARIO_LIBRARY["VOLDEMORT"]
    report = calc.calculate_similarity(sirius, voldemort)
    assert report.is_match is False
    assert report.similarity < 0.85


# ── Token arithmetic with new tokens ─────────────────────────────────────────

def test_morsmordre_dominates_over_anomaly():
    """morsmordre (0.95) has higher weight than anomaly (0.15); must dominate."""
    assert TOKEN_WEIGHTS["morsmordre"] > TOKEN_WEIGHTS["anomaly"]


def test_imperius_dominates_over_gate_on():
    """imperius (0.88) has lower weight than gate-on (0.90); gate-on still dominates raw."""
    assert TOKEN_WEIGHTS["gate-on"] > TOKEN_WEIGHTS["imperius"]


def test_protego_weight_ordering():
    """protego (0.75) sits between decorated (0.72) and legilimens (0.80)."""
    assert TOKEN_WEIGHTS["decorated"] < TOKEN_WEIGHTS["protego"] < TOKEN_WEIGHTS["legilimens"]


def test_freedom_signal_weight_ordering():
    """freedom-signal (0.82) sits between legilimens (0.80) and bio-signal (0.85)."""
    assert TOKEN_WEIGHTS["legilimens"] < TOKEN_WEIGHTS["freedom-signal"] < TOKEN_WEIGHTS["bio-signal"]


# ── Imperius gate state integration ──────────────────────────────────────────

def test_compute_imperius_sets_compromised_gate_state():
    """When imperius + gate-on are both active, compute() must return COMPROMISED."""
    calc = TokenTypeCalculator()
    calc.active_tokens = {"transistor", "gate-on", "imperius"}
    result = calc.compute()
    assert result["gate_state"] == "COMPROMISED"


def test_compute_gate_state_armed_without_imperius():
    """gate-on without imperius must still return ARMED."""
    calc = TokenTypeCalculator()
    calc.active_tokens = {"transistor", "gate-on"}
    result = calc.compute()
    assert result["gate_state"] == "ARMED"


def test_compute_dark_mark_state_in_result():
    """compute() must always include dark_mark_state key in return dict."""
    calc = TokenTypeCalculator()
    result = calc.compute()
    assert "dark_mark_state" in result


def test_compute_freedom_override_in_result():
    """compute() must always include freedom_override key in return dict."""
    calc = TokenTypeCalculator()
    result = calc.compute()
    assert "freedom_override" in result


# ── New scenario library size ─────────────────────────────────────────────────

def test_scenario_library_has_23_entries():
    """Original 15 entries + 8 new = 23 total."""
    assert len(SCENARIO_LIBRARY) == 23
