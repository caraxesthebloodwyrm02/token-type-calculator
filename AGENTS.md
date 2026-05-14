# AGENTS.md — token-type-calculator

Token signal calculator with four surfaces: FastAPI server, Rich CLI, standalone browser dashboard, and SQLite trajectory store. Python ≥ 3.14. Package manager: `uv`.

---

## Current state

**Phase:** Open development — foundational surfaces complete.

- All tests green (`uv run pytest`; **71** tests)
- All four surfaces operational: API, CLI, browser dashboard, batch client
- Fingerprint + similarity layer (`SCENARIO_LIBRARY` drives semantic search)
- Dashboard constants generated from `canonical_library.py` → `dashboard_constants.generated.js` (see Build & test)

---

## Build & test

```bash
# Install deps (includes dev group: pytest, ruff, basedpyright)
uv sync --all-groups

# Run tests
uv run pytest

# Lint
uv run ruff check .

# Type-check
uv run basedpyright

# CI: GitHub Actions runs ruff, basedpyright, pytest, regenerates
# `dashboard_constants.generated.js`, then `git diff --exit-code` on that file so edits
# to canonical_library.py cannot merge without a fresh sync.

# Regenerate browser constants after editing TOKEN_* / SCENARIO_LIBRARY in canonical_library.py
uv run python scripts/sync_dashboard_constants.py

# API server
uv run uvicorn api:app --host 0.0.0.0 --port 8000

# CLI
uv run python main.py relief   # or: not | moony | compare | wikidex | tui | dashboard

# Batch client (requires API server running)
uv run python client.py
```

Browser dashboard: open `index.html` directly in a browser (no server needed; requires Chrome 111+ / Firefox 113+ / Safari 16.2+ for `color-mix()`). Keep `dashboard_constants.generated.js` next to `index.html` (run the sync script above after library edits).

### Merge gate (pull requests)

The **Merge Gate (Every PR)** criteria live only in [`.github/pull_request_template.md`](.github/pull_request_template.md) (single source of truth). Opening a PR pre-fills those checkboxes on GitHub. Before marking a PR ready, merging, or recommending merge, satisfy **every** item there — same bar for humans and agents.

Full lifecycle (branching, pre-PR gates, review, merge, post-merge): [PR_OPERATIONS_PLAYBOOK.md](PR_OPERATIONS_PLAYBOOK.md).

---

## Architecture

| File | Role |
|------|------|
| `canonical_library.py` | Token visuals, weights, zones, and `SCENARIO_LIBRARY` — source for dashboard JS emission |
| `calculator.py` | Core engine — computation, gates, boundary detection, fingerprint derivation (re-exports library names) |
| `design.py` | All dataclasses and enums (`TokenType`, `BoundaryResult`, `ClaimedValue`, `Exchange`, etc.) |
| `scenarios.py` | Shared preset calculators for CLI + API (`/scenarios/moony`) |
| `api.py` | FastAPI routes wrapping calculator; lifespan calls `init_db()` |
| `main.py` | Rich CLI dispatcher — imports presets from `scenarios.py` |
| `client.py` | Batch test client — generates exactly 50 canonical scenarios, posts to `/compute` |
| `storage.py` | SQLite layer — `init_db()`, `save_request()`, `read_trajectory()` |
| `marauders_map.py` | Reads `compute_requests` trajectory; renders fingerprint similarity scores |
| `wikidex.py` | Pokédex-style scanner categorizing artifacts into 9 cognition patterns |
| `scripts/sync_dashboard_constants.py` | Writes `dashboard_constants.generated.js` from `canonical_library.py` |
| `dashboard_constants.generated.js` | Browser `TOKEN_*`, zones, `SCENARIO_LIBRARY` (generated; do not hand-edit) |

Reference docs: [DESIGN.md](DESIGN.md) · [ROUTINE.md](ROUTINE.md) · [docs/lore/WATERFALL.md](docs/lore/WATERFALL.md)

---

## Key conventions

**Token weights** (in `canonical_library.py`, used by `calculator.py`):

| Token | Weight |
|-------|--------|
| TRANSISTOR | 1.0 |
| GATE_ON | 0.9 |
| BIO_SIGNAL | 0.85 |
| DECORATED | 0.72 |
| AMBIENT | 0.45 |
| ANOMALY | 0.15 |
| GATE_OFF | 0.10 |

**Zones:**
- Buildup: steps 0–43 (intensity multiplier active)
- Silence: steps 44–47 (multiplier = 0.0 → strength always 0)
- Drop: steps 48–67 (multiplier = 1.0)

**No-take boundary:** fires when `engagement_cost > 0 AND service_value == 0`; forces `is_anomaly=True`.

**Gate states:** `ARMED` (gate-on before fire step), `UNARMED` (gate-off at fire step), `N/A` (no gate tokens).

**DB:** `token_calc.db`, table `compute_requests`. Timestamp stored as ISO-8601 UTC. `active_tokens` sorted before serialization. Use `tmp_path` fixture for ephemeral DB in tests.

**Fingerprint scenarios:** **`SCENARIO_LIBRARY`** in `canonical_library.py` (**23** named fingerprints for semantic search — baseline + extended roster).

**Scopes:** BLACK (MOONY+TONKS > 0.8), PHOENIX (8-member canonical Order — MOONY, TONKS, PRONGS, PADFOOT, SSSEVERUS, LILY, DUMBLEDORE, MOODY)

---

## Test layout

```
tests/
  test_calculator.py   # Core engine: boundary rejection, gate states, bio-signal integration
  test_storage.py      # init_db idempotency, save/read round-trip
  test_client.py       # 50-scenario batch, error handling (400/500/ConnectionError)
  test_html_smoke.py   # Browser smoke tests
test_moony_sim.py      # Moony similarity simulation (top-level)
```

No custom pytest marks. HTTP responses mocked via `_mock_response` helper.
