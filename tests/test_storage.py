import json
import sqlite3

import pytest

from calculator import TokenTypeCalculator
from storage import init_db, save_request


def _make_no_take_result():
    calc = TokenTypeCalculator()
    calc.toggle_token("bio-signal")
    calc.params["engagement_cost"] = 1.0
    calc.params["service_value"] = 0.0
    return calc.compute()


def _make_open_result():
    calc = TokenTypeCalculator()
    calc.toggle_token("gate-on")
    calc.params["engagement_cost"] = 0.5
    calc.params["service_value"] = 0.9
    return calc.compute()


def _no_take_params():
    return {
        "active_tokens": ["bio-signal", "transistor"],
        "zone": "buildup",
        "intensity": 0.69,
        "momentum": 1.0,
        "score": 0.81,
        "drift": 0.08,
        "engagement_cost": 1.0,
        "service_value": 0.0,
    }


def _open_params():
    return {
        "active_tokens": ["gate-on", "transistor"],
        "zone": "buildup",
        "intensity": 0.69,
        "momentum": 1.0,
        "score": 0.81,
        "drift": 0.08,
        "engagement_cost": 0.5,
        "service_value": 0.9,
    }


def test_init_db_idempotent(tmp_path):
    db = str(tmp_path / "test.db")
    init_db(db)
    init_db(db)  # second call must not raise
    with sqlite3.connect(db) as conn:
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "compute_requests" in tables


def test_save_request_returns_id(tmp_path):
    db = str(tmp_path / "test.db")
    init_db(db)
    result = _make_no_take_result()
    row_id = save_request("/compute", _no_take_params(), result, 12.5, db_path=db)
    assert isinstance(row_id, int)
    assert row_id > 0


def test_save_request_round_trip(tmp_path):
    db = str(tmp_path / "test.db")
    init_db(db)
    result = _make_no_take_result()
    row_id = save_request("/compute", _no_take_params(), result, 5.0, db_path=db)

    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT is_no_take, boundary_status FROM compute_requests WHERE id = ?",
            (row_id,),
        ).fetchone()

    assert row is not None
    assert row[0] == 1
    assert row[1] == "NO-TAKE (NOT)"


def test_active_tokens_sorted(tmp_path):
    db = str(tmp_path / "test.db")
    init_db(db)
    params = _no_take_params()
    params["active_tokens"] = ["transistor", "bio-signal"]  # unsorted insertion order
    result = _make_no_take_result()
    row_id = save_request("/compute", params, result, 1.0, db_path=db)

    with sqlite3.connect(db) as conn:
        stored = conn.execute(
            "SELECT active_tokens FROM compute_requests WHERE id = ?", (row_id,)
        ).fetchone()[0]

    tokens = json.loads(stored)
    assert tokens == sorted(tokens)
