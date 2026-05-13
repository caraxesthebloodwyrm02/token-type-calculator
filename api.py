import os
import time
from contextlib import asynccontextmanager
from typing import Any, Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, field_validator

from calculator import SCENARIO_LIBRARY, TOKEN_WEIGHTS, TokenTypeCalculator
from contracts import OperatorState
from design import (
    MOONY_SCORE_THRESHOLD,
    PHOENIX_CORE_SCORE,
    PRONGS_PRESENCE_THRESHOLD,
    SSSEVERUS_CLARITY_GAP,
    TONKS_SCORE_THRESHOLD,
)
from scenarios import run_moony_scenario
from storage import init_db, read_trajectory, save_request

ZoneName = Literal["buildup", "silence", "drop"]


class ComputeRequest(BaseModel):
    active_tokens: list[str] = Field(default_factory=lambda: ["transistor"], min_length=1)
    zone: ZoneName = "buildup"
    intensity: float = 0.69
    momentum: float = 1.0
    score: float = 0.81
    drift: float = 0.08
    engagement_cost: float = 0.0
    service_value: float = 0.0
    operator_state: OperatorState | None = None

    @field_validator("active_tokens")
    @classmethod
    def tokens_must_be_registered(cls, tokens: list[str]) -> list[str]:
        unknown = [t for t in tokens if t not in TOKEN_WEIGHTS]
        if unknown:
            raise ValueError(f"invalid tokens: {', '.join(unknown)}")
        return tokens


class VisualStateModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    face: object
    air: object


class AudioSignalModel(BaseModel):
    text: str
    voice_id: str
    fidelity: float
    resonance: dict[str, float]
    is_anomaly: bool
    timestamp: str


class FingerprintModel(BaseModel):
    pressure: float
    clarity: float
    movement: str
    dominant_type: str
    is_no_take: bool


class ComparisonReportModel(BaseModel):
    similarity: float
    drift_magnitude: float
    qualitative_shift: str
    is_match: bool


class ComputeResponse(BaseModel):
    dominant: str
    dom_color: str
    gate_state: str
    gate_color: str
    fired_val: str
    fired_color: str
    is_anomaly: bool
    strength: float
    total_weight: float
    transform_rate: float
    stability: str
    barter_target: str | None
    is_no_take: bool
    boundary_status: str
    boundary_color: str
    air_movement: str
    air_color: str
    air_pressure: float
    air_clarity: float
    visual_state: VisualStateModel
    audio_signal: AudioSignalModel
    fingerprint: FingerprintModel
    story: str | None = None
    memory_candidate: bool = False
    paths: list[str] | None = None
    marauder_trajectory: dict | None = None
    patronus_state: dict | None = None


def verify_api_key(x_api_key: str | None = Header(None)) -> str | None:
    expected = os.environ.get("TOKEN_CALC_API_KEY")
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing API key")
    return x_api_key


def _apply_request(calc: TokenTypeCalculator, payload: ComputeRequest) -> None:
    """Apply ComputeRequest fields onto a fresh TokenTypeCalculator instance."""
    calc.active_tokens = set(payload.active_tokens)
    calc.zone = payload.zone
    calc.sync_zone_from_step = False
    calc.params["intensity"] = payload.intensity
    calc.params["momentum"] = payload.momentum
    calc.params["score"] = payload.score
    calc.params["drift"] = payload.drift
    calc.params["engagement_cost"] = payload.engagement_cost
    calc.params["service_value"] = payload.service_value


def narrate_shift(result: dict, closest_scenario: str | None = None) -> str:
    """Synthesize a narrative 'Vision' for the current state shift."""
    fp = result["fingerprint"]
    boundary = result["boundary_status"]

    parts = []
    if result.get("patronus_state"):
        parts.append(
            "The serpent charges through the cold. Engagement and service are both full — "
            "the NO-TAKE boundary has been inverted. Expecto Patronum."
        )
    elif result["is_no_take"]:
        parts.append(
            "The boundary has been reached: engagement is high but service is absent. "
            "The NO-TAKE rule is absolute."
        )
    else:
        parts.append(f"The exchange is {boundary.lower()}.")

    if closest_scenario:
        parts.append(f"The shift aligns with the {closest_scenario} archetype.")

    if fp.movement == "TURBULENT":
        parts.append("The air is turbulent; a qualitative transformation is imminent.")
    elif fp.movement == "GUST":
        parts.append("A gust is present—push and pull forces are active.")

    return " ".join(parts)


class CompareRequest(BaseModel):
    a: ComputeRequest
    b: ComputeRequest


class CompareResponse(BaseModel):
    a: ComputeResponse
    b: ComputeResponse
    report: ComparisonReportModel


class SearchResponse(BaseModel):
    query_result: ComputeResponse
    closest_scenario: str
    report: ComparisonReportModel


class HealthResponse(BaseModel):
    status: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Token Type Calculator API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/compute", response_model=ComputeResponse, dependencies=[Depends(verify_api_key)])
def compute(payload: ComputeRequest) -> dict:
    calc = TokenTypeCalculator()
    _apply_request(calc, payload)

    t0 = time.perf_counter()
    result = calc.compute()
    duration_ms = (time.perf_counter() - t0) * 1000

    fp = result["fingerprint"]
    result["memory_candidate"] = (
        fp.pressure > 0.6 and 0.3 <= fp.clarity <= 0.7 and fp.movement == "TURBULENT"
    )

    result["paths"] = None
    result["marauder_trajectory"] = None

    if payload.operator_state == "INTENTIONAL":
        trajectory = read_trajectory(limit=10)
        search = calc.semantic_search(fp)
        result["paths"] = [search["scenario"]] if search["scenario"] else []
        result["trajectory"] = trajectory[:5]

    elif payload.operator_state == "BLACK":
        trajectory = read_trajectory(limit=10)
        marauder_keys = {"MOONY", "TONKS", "PRONGS", "PADFOOT", "WORMTAIL", "SSSEVERUS", "LILY"}
        scores = {
            name: calc.calculate_similarity(fp, SCENARIO_LIBRARY[name]).similarity
            for name in marauder_keys
        }
        closest = max(scores, key=lambda k: scores[k])
        result["marauder_trajectory"] = {
            "closest": closest,
            "scores": {k: round(v, 4) for k, v in scores.items()},
            "gate_history_coherent": all(k in SCENARIO_LIBRARY for k in ("PADFOOT", "WORMTAIL")),
            "prongs_present": scores.get("PRONGS", 0.0) >= PRONGS_PRESENCE_THRESHOLD,
            "trajectory_length": len(trajectory),
        }

    elif payload.operator_state == "SSSEVERUS":
        trajectory = read_trajectory(limit=10)
        snapes = calc.calculate_similarity(fp, SCENARIO_LIBRARY["SSSEVERUS"])
        patronus_gap = abs(fp.clarity - 1.0)
        result["marauder_trajectory"] = {
            "closest": "SSSEVERUS",
            "scores": {"SSSEVERUS": round(snapes.similarity, 4)},
            "clarity_gap": round(patronus_gap, 4),
            "inherited_anchor": patronus_gap >= SSSEVERUS_CLARITY_GAP,
            "trajectory_length": len(trajectory),
        }

    elif payload.operator_state == "LILY":
        trajectory = read_trajectory(limit=10)
        lily_sim = calc.calculate_similarity(fp, SCENARIO_LIBRARY["LILY"])
        at_perfect_cast = abs(fp.pressure - 1.0) < 0.01 and abs(fp.clarity - 1.0) < 0.01
        result["marauder_trajectory"] = {
            "closest": "LILY",
            "scores": {"LILY": round(lily_sim.similarity, 4)},
            "at_perfect_cast": at_perfect_cast,
            "trajectory_length": len(trajectory),
        }

    elif payload.operator_state == "PHOENIX":
        trajectory = read_trajectory(limit=10)
        phoenix_members = {"MOONY", "TONKS", "PRONGS", "PADFOOT", "SSSEVERUS", "LILY", "DUMBLEDORE", "MOODY"}
        scores = {
            name: calc.calculate_similarity(fp, SCENARIO_LIBRARY[name]).similarity
            for name in phoenix_members
        }
        closest = max(scores, key=lambda k: scores[k])
        active = {k: v for k, v in scores.items() if v >= PHOENIX_CORE_SCORE}
        result["marauder_trajectory"] = {
            "closest": closest,
            "scores": {k: round(v, 4) for k, v in scores.items()},
            "phoenix_active": list(active.keys()),
            "phoenix_strength": round(len(active) / len(phoenix_members), 4),
            "trajectory_length": len(trajectory),
        }

    elif payload.operator_state == "MAP":
        # Full map view for the API
        trajectory = read_trajectory(limit=10)
        scores = {
            name: calc.calculate_similarity(fp, scenario).similarity
            for name, scenario in SCENARIO_LIBRARY.items()
        }
        moony_high = scores.get("MOONY", 0.0) > MOONY_SCORE_THRESHOLD
        tonks_high = scores.get("TONKS", 0.0) > TONKS_SCORE_THRESHOLD
        result["marauder_trajectory"] = {
            "all_scores": {k: round(v, 4) for k, v in scores.items()},
            "trajectory": trajectory,
            "black_scope_active": moony_high and tonks_high,
        }

    # Add narrative story
    closest = None
    if result.get("marauder_trajectory") and "closest" in result["marauder_trajectory"]:
        closest = result["marauder_trajectory"]["closest"]
    result["story"] = narrate_shift(result, closest)

    save_request("/compute", payload.model_dump(), result, duration_ms)
    return result


@app.post("/compare", response_model=CompareResponse, dependencies=[Depends(verify_api_key)])
def compare(payload: CompareRequest) -> dict:
    calc = TokenTypeCalculator()

    # Compute A
    calc_a = TokenTypeCalculator()
    _apply_request(calc_a, payload.a)
    t0 = time.perf_counter()
    res_a = calc_a.compute()
    save_request("/compare", payload.a.model_dump(), res_a, (time.perf_counter() - t0) * 1000)

    # Compute B
    calc_b = TokenTypeCalculator()
    _apply_request(calc_b, payload.b)
    t0 = time.perf_counter()
    res_b = calc_b.compute()
    save_request("/compare", payload.b.model_dump(), res_b, (time.perf_counter() - t0) * 1000)

    report = calc.calculate_similarity(res_a['fingerprint'], res_b['fingerprint'])

    # Story for comparisons is the qualitative shift
    res_a["story"] = narrate_shift(res_a)
    res_b["story"] = narrate_shift(res_b)

    return {
        "a": res_a,
        "b": res_b,
        "report": report
    }


@app.get("/scenarios/moony", response_model=ComputeResponse, dependencies=[Depends(verify_api_key)])
def moony_scenario() -> dict[str, Any]:
    calc = run_moony_scenario()
    moony_params = {
        "active_tokens": list(calc.active_tokens),
        "zone": calc.zone,
        "intensity": calc.params["intensity"],
        "momentum": calc.params["momentum"],
        "score": calc.params["score"],
        "drift": calc.params["drift"],
        "engagement_cost": calc.params["engagement_cost"],
        "service_value": calc.params["service_value"],
    }
    t0 = time.perf_counter()
    result = calc.compute()
    result["story"] = narrate_shift(result, "MOONY")
    save_request("/scenarios/moony", moony_params, result, (time.perf_counter() - t0) * 1000)
    return result


@app.post("/search", response_model=SearchResponse, dependencies=[Depends(verify_api_key)])
def search(payload: ComputeRequest) -> dict:
    calc = TokenTypeCalculator()
    _apply_request(calc, payload)
    t0 = time.perf_counter()
    res = calc.compute()
    save_request("/search", payload.model_dump(), res, (time.perf_counter() - t0) * 1000)

    search_res = calc.semantic_search(res['fingerprint'])
    res["story"] = narrate_shift(res, search_res['scenario'])

    return {
        "query_result": res,
        "closest_scenario": search_res['scenario'],
        "report": search_res['report']
    }
