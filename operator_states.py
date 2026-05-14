"""Operator-state handlers for `/compute`.

Each handler takes the calculator, the request fingerprint, and a pre-read
trajectory, and returns a partial result dict that the route merges into the
response. Adding a new operator state is a one-function add plus a registry
entry — `api.py` does not need to change.
"""

from collections.abc import Callable
from typing import Any

from calculator import SCENARIO_LIBRARY, TokenTypeCalculator
from contracts import OperatorState
from design import (
    MOONY_SCORE_THRESHOLD,
    PHOENIX_CORE_SCORE,
    PRONGS_PRESENCE_THRESHOLD,
    SSSEVERUS_CLARITY_GAP,
    TONKS_SCORE_THRESHOLD,
    Fingerprint,
)

OperatorStateHandler = Callable[
    [TokenTypeCalculator, Fingerprint, list[dict[str, Any]]],
    dict[str, Any],
]


def _intentional(
    calc: TokenTypeCalculator, fp: Fingerprint, trajectory: list[dict[str, Any]]
) -> dict[str, Any]:
    search = calc.semantic_search(fp)
    return {
        "paths": [search["scenario"]] if search["scenario"] else [],
        "trajectory": trajectory[:5],
    }


def _black(
    calc: TokenTypeCalculator, fp: Fingerprint, trajectory: list[dict[str, Any]]
) -> dict[str, Any]:
    marauder_keys = {"MOONY", "TONKS", "PRONGS", "PADFOOT", "WORMTAIL", "SSSEVERUS", "LILY"}
    scores = {
        name: calc.calculate_similarity(fp, SCENARIO_LIBRARY[name]).similarity
        for name in marauder_keys
    }
    closest = max(scores, key=lambda k: scores[k])
    return {
        "marauder_trajectory": {
            "closest": closest,
            "scores": {k: round(v, 4) for k, v in scores.items()},
            "gate_history_coherent": all(k in SCENARIO_LIBRARY for k in ("PADFOOT", "WORMTAIL")),
            "prongs_present": scores.get("PRONGS", 0.0) >= PRONGS_PRESENCE_THRESHOLD,
            "trajectory_length": len(trajectory),
        }
    }


def _ssseverus(
    calc: TokenTypeCalculator, fp: Fingerprint, trajectory: list[dict[str, Any]]
) -> dict[str, Any]:
    snapes = calc.calculate_similarity(fp, SCENARIO_LIBRARY["SSSEVERUS"])
    patronus_gap = abs(fp.clarity - 1.0)
    return {
        "marauder_trajectory": {
            "closest": "SSSEVERUS",
            "scores": {"SSSEVERUS": round(snapes.similarity, 4)},
            "clarity_gap": round(patronus_gap, 4),
            "inherited_anchor": patronus_gap >= SSSEVERUS_CLARITY_GAP,
            "trajectory_length": len(trajectory),
        }
    }


def _lily(
    calc: TokenTypeCalculator, fp: Fingerprint, trajectory: list[dict[str, Any]]
) -> dict[str, Any]:
    lily_sim = calc.calculate_similarity(fp, SCENARIO_LIBRARY["LILY"])
    at_perfect_cast = abs(fp.pressure - 1.0) < 0.01 and abs(fp.clarity - 1.0) < 0.01
    return {
        "marauder_trajectory": {
            "closest": "LILY",
            "scores": {"LILY": round(lily_sim.similarity, 4)},
            "at_perfect_cast": at_perfect_cast,
            "trajectory_length": len(trajectory),
        }
    }


def _phoenix(
    calc: TokenTypeCalculator, fp: Fingerprint, trajectory: list[dict[str, Any]]
) -> dict[str, Any]:
    phoenix_members = {"MOONY", "TONKS", "PRONGS", "PADFOOT", "SSSEVERUS", "LILY", "DUMBLEDORE", "MOODY"}
    scores = {
        name: calc.calculate_similarity(fp, SCENARIO_LIBRARY[name]).similarity
        for name in phoenix_members
    }
    closest = max(scores, key=lambda k: scores[k])
    active = {k: v for k, v in scores.items() if v >= PHOENIX_CORE_SCORE}
    return {
        "marauder_trajectory": {
            "closest": closest,
            "scores": {k: round(v, 4) for k, v in scores.items()},
            "phoenix_active": list(active.keys()),
            "phoenix_strength": round(len(active) / len(phoenix_members), 4),
            "trajectory_length": len(trajectory),
        }
    }


def _map_view(
    calc: TokenTypeCalculator, fp: Fingerprint, trajectory: list[dict[str, Any]]
) -> dict[str, Any]:
    scores = {
        name: calc.calculate_similarity(fp, scenario).similarity
        for name, scenario in SCENARIO_LIBRARY.items()
    }
    moony_high = scores.get("MOONY", 0.0) > MOONY_SCORE_THRESHOLD
    tonks_high = scores.get("TONKS", 0.0) > TONKS_SCORE_THRESHOLD
    return {
        "marauder_trajectory": {
            "all_scores": {k: round(v, 4) for k, v in scores.items()},
            "trajectory": trajectory,
            "black_scope_active": moony_high and tonks_high,
        }
    }


HANDLERS: dict[OperatorState, OperatorStateHandler] = {
    "INTENTIONAL": _intentional,
    "BLACK": _black,
    "SSSEVERUS": _ssseverus,
    "LILY": _lily,
    "PHOENIX": _phoenix,
    "MAP": _map_view,
}


def apply_operator_state(
    calc: TokenTypeCalculator,
    fp: Fingerprint,
    state: OperatorState | None,
    trajectory: list[dict[str, Any]],
) -> dict[str, Any]:
    """Dispatch to the handler for `state`. Returns {} when no handler matches."""
    if state is None:
        return {}
    handler = HANDLERS.get(state)
    if handler is None:
        return {}
    return handler(calc, fp, trajectory)
