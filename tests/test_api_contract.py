"""HTTP-adjacent contract tests without TestClient (no httpx dev dependency).

Calls FastAPI route handlers directly and validates ComputeRequest with Pydantic.
"""

import pytest
from pydantic import ValidationError

import api as api_module
from api import ComputeRequest, compute


def test_compute_zone_silence_authoritative():
    """Request zone wins over default params['step'] (buildup range)."""
    result = compute(
        ComputeRequest(
            active_tokens=["transistor"],
            zone="silence",
            engagement_cost=0.2,
            service_value=0.3,
        )
    )
    assert result["is_anomaly"] is True
    assert result["strength"] == 0.0


def test_compute_zone_drop_authoritative():
    result = compute(
        ComputeRequest(
            active_tokens=["transistor"],
            zone="drop",
            intensity=1.0,
            momentum=1.0,
            score=1.0,
            engagement_cost=0.0,
            service_value=0.0,
        )
    )
    assert result["strength"] > 0.0


def test_compute_request_rejects_unknown_operator_state():
    with pytest.raises(ValidationError):
        ComputeRequest.model_validate(
            {"active_tokens": ["transistor"], "operator_state": "NOT_A_SUPPORTED_STATE"}
        )


def test_compute_operator_state_map_branch(monkeypatch):
    monkeypatch.setattr(api_module, "read_trajectory", lambda **kwargs: [])
    result = compute(
        ComputeRequest(
            active_tokens=["transistor"],
            zone="buildup",
            operator_state="MAP",
        )
    )
    assert result["marauder_trajectory"] is not None
    assert "all_scores" in result["marauder_trajectory"]


# ── operator_state branch coverage ───────────────────────────────────────────

def test_compute_operator_state_intentional_returns_paths(monkeypatch):
    """INTENTIONAL handler sets paths from semantic_search; marauder_trajectory stays None."""
    monkeypatch.setattr(api_module, "read_trajectory", lambda **kwargs: [])
    result = compute(
        ComputeRequest(active_tokens=["transistor"], zone="buildup", operator_state="INTENTIONAL")
    )
    assert isinstance(result["paths"], list)
    assert result.get("marauder_trajectory") is None


def test_compute_operator_state_black_returns_marauder_scores(monkeypatch):
    """BLACK handler scores all 7 marauders and identifies the closest."""
    monkeypatch.setattr(api_module, "read_trajectory", lambda **kwargs: [])
    result = compute(
        ComputeRequest(active_tokens=["transistor"], zone="buildup", operator_state="BLACK")
    )
    mt = result["marauder_trajectory"]
    assert mt is not None
    expected_members = {"MOONY", "TONKS", "PRONGS", "PADFOOT", "WORMTAIL", "SSSEVERUS", "LILY"}
    assert set(mt["scores"].keys()) == expected_members
    assert mt["closest"] in expected_members
    assert mt["gate_history_coherent"] is True
    assert isinstance(mt["prongs_present"], bool)


def test_compute_operator_state_ssseverus_anchors_to_snape(monkeypatch):
    """SSSEVERUS handler fixes closest to SSSEVERUS and exposes clarity_gap."""
    monkeypatch.setattr(api_module, "read_trajectory", lambda **kwargs: [])
    result = compute(
        ComputeRequest(active_tokens=["transistor"], zone="buildup", operator_state="SSSEVERUS")
    )
    mt = result["marauder_trajectory"]
    assert mt is not None
    assert mt["closest"] == "SSSEVERUS"
    assert set(mt["scores"].keys()) == {"SSSEVERUS"}
    assert "clarity_gap" in mt
    assert "inherited_anchor" in mt
    assert isinstance(mt["inherited_anchor"], bool)


def test_compute_operator_state_lily_at_perfect_cast(monkeypatch):
    """LILY handler sets at_perfect_cast=True only when pressure≈1.0 and clarity≈1.0."""
    monkeypatch.setattr(api_module, "read_trajectory", lambda **kwargs: [])

    result_perfect = compute(
        ComputeRequest(
            active_tokens=["transistor"],
            zone="drop",
            intensity=1.0,
            momentum=1.0,
            score=1.0,
            engagement_cost=1.0,
            service_value=1.0,
            operator_state="LILY",
        )
    )
    assert result_perfect["marauder_trajectory"]["closest"] == "LILY"
    assert result_perfect["marauder_trajectory"]["at_perfect_cast"] is True

    result_off = compute(
        ComputeRequest(
            active_tokens=["transistor"],
            zone="buildup",
            operator_state="LILY",
        )
    )
    assert result_off["marauder_trajectory"]["at_perfect_cast"] is False


def test_compute_operator_state_phoenix_scores_all_members(monkeypatch):
    """PHOENIX handler scores all 8 Order members and reports phoenix_strength."""
    monkeypatch.setattr(api_module, "read_trajectory", lambda **kwargs: [])
    result = compute(
        ComputeRequest(active_tokens=["transistor"], zone="buildup", operator_state="PHOENIX")
    )
    mt = result["marauder_trajectory"]
    assert mt is not None
    expected_members = {"MOONY", "TONKS", "PRONGS", "PADFOOT", "SSSEVERUS", "LILY", "DUMBLEDORE", "MOODY"}
    assert set(mt["scores"].keys()) == expected_members
    assert mt["closest"] in expected_members
    assert isinstance(mt["phoenix_active"], list)
    assert 0.0 <= mt["phoenix_strength"] <= 1.0
    assert mt["phoenix_strength"] == round(len(mt["phoenix_active"]) / len(expected_members), 4)
