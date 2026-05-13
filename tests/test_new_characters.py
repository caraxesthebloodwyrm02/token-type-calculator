"""Tests for the 8 new SCENARIO_LIBRARY entries added in Phase 2.

Verifies fingerprint coordinates, dominant_type, movement, and is_no_take
for each new character. Does not test engine computation — just library integrity.
"""
import pytest
from calculator import SCENARIO_LIBRARY


# ── Dark Mark Roster ──────────────────────────────────────────────────────────

def test_voldemort_fingerprint():
    fp = SCENARIO_LIBRARY["VOLDEMORT"]
    assert fp.pressure == 1.0
    assert fp.clarity == 0.0
    assert fp.movement == "TURBULENT"
    assert fp.dominant_type == "MORSMORDRE"
    assert fp.is_no_take is True


def test_bellatrix_fingerprint():
    fp = SCENARIO_LIBRARY["BELLATRIX"]
    assert fp.pressure == 1.0
    assert fp.clarity == 0.2
    assert fp.movement == "GUST"
    assert fp.dominant_type == "ANOMALY"
    assert fp.is_no_take is True


def test_regulus_fingerprint():
    """Regulus is a former Death Eater who chose differently — NOT a no-take."""
    fp = SCENARIO_LIBRARY["REGULUS"]
    assert fp.pressure == 0.9
    assert fp.clarity == 0.7
    assert fp.movement == "DRIFT"
    assert fp.dominant_type == "BIO_SIGNAL"
    assert fp.is_no_take is False


# ── Hogwarts Faculty ──────────────────────────────────────────────────────────

def test_mcgonagall_fingerprint():
    fp = SCENARIO_LIBRARY["MCGONAGALL"]
    assert fp.pressure == 0.7
    assert fp.clarity == 0.9
    assert fp.movement == "DRIFT"
    assert fp.dominant_type == "INTENTIONAL"
    assert fp.is_no_take is False


def test_slughorn_fingerprint():
    fp = SCENARIO_LIBRARY["SLUGHORN"]
    assert fp.pressure == 0.4
    assert fp.clarity == 0.5
    assert fp.movement == "GUST"
    assert fp.dominant_type == "DECORATED"
    assert fp.is_no_take is False


# ── House of Black ────────────────────────────────────────────────────────────

def test_sirius_black_fingerprint():
    """SIRIUS_BLACK is a separate entry from PADFOOT — the man, not the animagus gate state."""
    fp = SCENARIO_LIBRARY["SIRIUS_BLACK"]
    assert fp.pressure == 0.9
    assert fp.clarity == 0.5
    assert fp.movement == "GUST"
    assert fp.dominant_type == "INTENTIONAL"
    assert fp.is_no_take is False


def test_kreacher_reclaimed_fingerprint():
    fp = SCENARIO_LIBRARY["KREACHER_RECLAIMED"]
    assert fp.pressure == 0.6
    assert fp.clarity == 0.7
    assert fp.movement == "DRIFT"
    assert fp.dominant_type == "BIO_SIGNAL"
    assert fp.is_no_take is False


# ── The Free Elf ──────────────────────────────────────────────────────────────

def test_dobby_fingerprint():
    fp = SCENARIO_LIBRARY["DOBBY"]
    assert fp.pressure == 0.8
    assert fp.clarity == 0.6
    assert fp.movement == "DRIFT"
    assert fp.dominant_type == "BIO_SIGNAL"
    assert fp.is_no_take is False


# ── Structural invariants ─────────────────────────────────────────────────────

def test_dark_mark_roster_all_present():
    """All 3 Dark Mark roster entries must exist in SCENARIO_LIBRARY."""
    for name in ["VOLDEMORT", "BELLATRIX", "REGULUS"]:
        assert name in SCENARIO_LIBRARY, f"{name} missing from SCENARIO_LIBRARY"


def test_new_characters_all_present():
    """All 5 non-dark-mark new characters must be in SCENARIO_LIBRARY."""
    for name in ["MCGONAGALL", "DOBBY", "SLUGHORN", "SIRIUS_BLACK", "KREACHER_RECLAIMED"]:
        assert name in SCENARIO_LIBRARY, f"{name} missing from SCENARIO_LIBRARY"


def test_sirius_padfoot_are_distinct():
    """SIRIUS_BLACK and PADFOOT must be separate entries with different fingerprints."""
    sirius = SCENARIO_LIBRARY["SIRIUS_BLACK"]
    padfoot = SCENARIO_LIBRARY["PADFOOT"]
    # Same ballpark pressure, different clarity and dominant_type
    assert sirius.dominant_type != padfoot.dominant_type
    assert sirius.clarity != padfoot.clarity


def test_no_take_characters_exactly():
    """Exactly VOLDEMORT and BELLATRIX from the new set are no-take."""
    new_entries = {
        "VOLDEMORT", "BELLATRIX", "REGULUS",
        "MCGONAGALL", "DOBBY", "SLUGHORN", "SIRIUS_BLACK", "KREACHER_RECLAIMED",
    }
    no_take_new = {n for n in new_entries if SCENARIO_LIBRARY[n].is_no_take}
    assert no_take_new == {"VOLDEMORT", "BELLATRIX"}
