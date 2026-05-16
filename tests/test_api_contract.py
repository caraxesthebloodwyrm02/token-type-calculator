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
