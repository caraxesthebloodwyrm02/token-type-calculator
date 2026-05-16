"""Tests for generate_marauders_map() with stubbed trajectory data."""

import marauders_map as mm_module
from calculator import SCENARIO_LIBRARY, TokenTypeCalculator
from design import Fingerprint
from marauders_map import generate_marauders_map


def _fake_trajectory():
    return [
        {
            "timestamp_utc": "2026-05-16T12:00:00Z",
            "dominant": "transistor",
            "air_pressure": 0.5,
            "air_clarity": 0.7,
            "air_movement": "steady",
            "is_no_take": 0,
        },
        {
            "timestamp_utc": "2026-05-16T12:01:00Z",
            "dominant": "ambient",
            "air_pressure": 0.6,
            "air_clarity": 0.8,
            "air_movement": "rising",
            "is_no_take": 0,
        },
    ]


def test_empty_trajectory_returns_blank(monkeypatch):
    monkeypatch.setattr(mm_module, "read_trajectory", lambda limit=10: [])
    result = generate_marauders_map()
    assert "map is blank" in result.lower()


def test_map_contains_expected_sections(monkeypatch):
    monkeypatch.setattr(mm_module, "read_trajectory", lambda limit=10: _fake_trajectory())
    result = generate_marauders_map()
    assert "THE MARAUDER'S MAP" in result
    assert "THE PACK:" in result
    assert "HALF-BLOOD PRINCE:" in result
    assert "THE ANCHOR:" in result
    assert "ORDER OF THE PHOENIX:" in result
    assert "DEATH EATER PROXIMITY:" in result
    assert "FOOTPRINTS" in result


def test_map_shows_marauder_names(monkeypatch):
    monkeypatch.setattr(mm_module, "read_trajectory", lambda limit=10: _fake_trajectory())
    result = generate_marauders_map()
    for name in ["MOONY", "TONKS", "PRONGS", "PADFOOT", "WORMTAIL"]:
        assert name in result


def test_map_shows_latest_trajectory_entry(monkeypatch):
    monkeypatch.setattr(mm_module, "read_trajectory", lambda limit=10: _fake_trajectory())
    result = generate_marauders_map()
    assert "2026-05-16T12:01:00Z" in result
    assert "ambient" in result


def test_ssseverus_clarity_gap(monkeypatch):
    monkeypatch.setattr(mm_module, "read_trajectory", lambda limit=10: _fake_trajectory())
    result = generate_marauders_map()
    assert "clarity_gap:" in result


def test_new_characters_section(monkeypatch):
    monkeypatch.setattr(mm_module, "read_trajectory", lambda limit=10: _fake_trajectory())
    result = generate_marauders_map()
    assert "HOGWARTS / HOUSE OF BLACK / THE FREE ELF:" in result
    for name in ["MCGONAGALL", "DOBBY", "SLUGHORN", "SIRIUS_BLACK", "KREACHER_RECLAIMED"]:
        assert name in result


def test_sirius_duality_annotation(monkeypatch):
    """SIRIUS duality line must contain the correct computed scores and their delta.

    Derives expected values using the same similarity path as generate_marauders_map()
    so a swap, wiring error, or delta arithmetic bug will cause a mismatch.
    """
    monkeypatch.setattr(mm_module, "read_trajectory", lambda limit=10: _fake_trajectory())

    latest = _fake_trajectory()[-1]
    current_fp = Fingerprint(
        pressure=latest["air_pressure"],
        clarity=latest["air_clarity"],
        movement=latest["air_movement"],
        dominant_type=latest["dominant"].upper(),
        is_no_take=bool(latest["is_no_take"]),
    )
    calc = TokenTypeCalculator()
    sirius_score = calc.calculate_similarity(current_fp, SCENARIO_LIBRARY["SIRIUS_BLACK"]).similarity
    padfoot_score = calc.calculate_similarity(current_fp, SCENARIO_LIBRARY["PADFOOT"]).similarity
    expected_delta = abs(sirius_score - padfoot_score)

    result = generate_marauders_map()

    assert f"SIRIUS_BLACK={sirius_score:.4f}" in result
    assert f"PADFOOT={padfoot_score:.4f}" in result
    assert f"delta={expected_delta:.4f}" in result
