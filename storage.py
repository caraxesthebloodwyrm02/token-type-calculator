"""SQLite persistence layer for the token type calculator.

Every /compute, /compare, /search, /scenarios/moony, and CLI scenario writes a
row here. read_trajectory() makes the resulting map readable by marauders_map.py
and by the INTENTIONAL / BLACK / MAP operator states in api.py.

See AUTHOR.md for conventions:
  - init_db is idempotent (safe to call twice).
  - active_tokens are sorted before serializing.
  - non-JSON dataclasses are normalized via dataclasses.asdict.
  - timestamp_utc is ISO-8601 UTC; the _utc suffix is load-bearing.
  - refusal is data: NO-TAKE rows are normal rows with is_no_take = 1.
"""

import dataclasses
import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any

DEFAULT_DB_PATH = os.environ.get("TOKEN_CALC_DB", "token_calc.db")


# ---------------------------------------------------------------------------
# JSON normalization
# ---------------------------------------------------------------------------

def _to_jsonable(obj: Any) -> Any:
    """Default encoder for dataclasses (Fingerprint, AudioSignal, Face, AirElement)
    and other non-JSON-native values that show up inside a compute result."""
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.asdict(obj)
    if isinstance(obj, set):
        return sorted(obj)
    if isinstance(obj, (datetime,)):
        return obj.isoformat()
    # Fall back to repr — preserves visibility without crashing the write.
    return repr(obj)


def _dumps(value: Any) -> str:
    return json.dumps(value, default=_to_jsonable, sort_keys=False)


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS compute_requests (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp_utc   TEXT    NOT NULL,
    endpoint        TEXT    NOT NULL,
    duration_ms     REAL    NOT NULL,

    -- surface signal: enough to draw a trajectory without parsing result_json
    active_tokens   TEXT    NOT NULL,   -- JSON array, sorted
    zone            TEXT,
    dominant        TEXT,
    gate_state      TEXT,
    fired_val       TEXT,
    is_anomaly      INTEGER NOT NULL DEFAULT 0,
    is_no_take      INTEGER NOT NULL DEFAULT 0,
    boundary_status TEXT,
    strength        REAL,
    transform_rate  REAL,
    stability       TEXT,
    air_movement    TEXT,
    air_pressure    REAL,
    air_clarity     REAL,

    -- full payloads, for replay and audit
    params_json     TEXT    NOT NULL,
    result_json     TEXT    NOT NULL
);
"""

_INDEX_TIMESTAMP = "CREATE INDEX IF NOT EXISTS idx_compute_requests_timestamp ON compute_requests(timestamp_utc);"
_INDEX_NO_TAKE = "CREATE INDEX IF NOT EXISTS idx_compute_requests_no_take ON compute_requests(is_no_take);"


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Create the compute_requests table if missing. Idempotent."""
    with sqlite3.connect(db_path) as conn:
        conn.executescript(_SCHEMA)
        conn.execute(_INDEX_TIMESTAMP)
        conn.execute(_INDEX_NO_TAKE)
        conn.commit()


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------

def _coerce_active_tokens(params: dict[str, Any]) -> list[str]:
    """Return active_tokens from params as a sorted list of strings.

    Sorted-on-write is asserted in tests/test_storage.py::test_active_tokens_sorted —
    insertion order is not meaningful and a stable order makes trajectory diffs readable.
    """
    raw = params.get("active_tokens", [])
    if raw is None:
        return []
    if isinstance(raw, (set, frozenset)):
        return sorted(raw)
    return sorted(str(t) for t in raw)


def save_request(
    endpoint: str,
    params: dict[str, Any],
    result: dict[str, Any],
    duration_ms: float,
    db_path: str = DEFAULT_DB_PATH,
) -> int:
    """Persist one compute request. Returns the new row id.

    `result` is expected to be the dict returned by TokenTypeCalculator.compute(),
    including the dataclass fields (fingerprint, audio_signal, visual_state).
    Those are normalized through dataclasses.asdict before being written to
    result_json so the row stays self-contained.
    """
    timestamp_utc = datetime.now(timezone.utc).isoformat()
    active_tokens = _coerce_active_tokens(params)

    # Surface signal — kept as real columns so trajectory queries don't have
    # to JSON-decode result_json for every row.
    is_anomaly = 1 if result.get("is_anomaly") else 0
    is_no_take = 1 if result.get("is_no_take") else 0

    row = (
        timestamp_utc,
        endpoint,
        float(duration_ms),

        _dumps(active_tokens),
        params.get("zone"),
        result.get("dominant"),
        result.get("gate_state"),
        result.get("fired_val"),
        is_anomaly,
        is_no_take,
        result.get("boundary_status"),
        result.get("strength"),
        result.get("transform_rate"),
        result.get("stability"),
        result.get("air_movement"),
        result.get("air_pressure"),
        result.get("air_clarity"),

        _dumps(params),
        _dumps(result),
    )

    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO compute_requests (
                timestamp_utc, endpoint, duration_ms,
                active_tokens, zone, dominant, gate_state, fired_val,
                is_anomaly, is_no_take, boundary_status,
                strength, transform_rate, stability,
                air_movement, air_pressure, air_clarity,
                params_json, result_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            row,
        )
        conn.commit()
        row_id = cur.lastrowid

    return int(row_id)


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

# Columns exposed by read_trajectory. marauders_map.py reads these fields by name
# (timestamp_utc, dominant, air_movement, air_pressure, air_clarity, is_no_take),
# so the contract is the keys of each returned dict.
_TRAJECTORY_COLUMNS = (
    "id",
    "timestamp_utc",
    "endpoint",
    "duration_ms",
    "zone",
    "dominant",
    "gate_state",
    "fired_val",
    "is_anomaly",
    "is_no_take",
    "boundary_status",
    "strength",
    "transform_rate",
    "stability",
    "air_movement",
    "air_pressure",
    "air_clarity",
    "active_tokens",
)


def read_trajectory(
    limit: int = 10,
    db_path: str = DEFAULT_DB_PATH,
) -> list[dict[str, Any]]:
    """Return up to `limit` most recent compute rows, ordered oldest → newest.

    Oldest-first so marauders_map.py can render footprints left-to-right and
    trajectory[-1] is the latest state. active_tokens is decoded back to a list.
    """
    if limit <= 0:
        return []

    columns = ", ".join(_TRAJECTORY_COLUMNS)
    query = f"""
        SELECT {columns}
        FROM compute_requests
        ORDER BY id DESC
        LIMIT ?;
    """

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, (limit,)).fetchall()

    out: list[dict[str, Any]] = []
    for row in reversed(rows):  # oldest first
        record = {col: row[col] for col in _TRAJECTORY_COLUMNS}
        try:
            record["active_tokens"] = json.loads(record["active_tokens"] or "[]")
        except (TypeError, json.JSONDecodeError):
            record["active_tokens"] = []
        out.append(record)
    return out


# ---------------------------------------------------------------------------
# Convenience aggregates (used by client.py summary, not asserted in tests)
# ---------------------------------------------------------------------------

def count_no_take(db_path: str = DEFAULT_DB_PATH) -> int:
    """Total number of rows where the boundary fired NO-TAKE."""
    with sqlite3.connect(db_path) as conn:
        (n,) = conn.execute(
            "SELECT COUNT(*) FROM compute_requests WHERE is_no_take = 1;"
        ).fetchone()
    return int(n)


def count_by_endpoint(db_path: str = DEFAULT_DB_PATH) -> dict[str, int]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT endpoint, COUNT(*) FROM compute_requests GROUP BY endpoint ORDER BY 2 DESC;"
        ).fetchall()
    return {endpoint: int(n) for endpoint, n in rows}
