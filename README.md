# Token Type Calculator

Signal calculator for typed token exchanges: a **standalone browser dashboard**, **FastAPI** API, **Rich CLI**, SQLite trajectory storage, and a **batch HTTP client**. Token weights, colors, zones, and fingerprint anchors live in `canonical_library.py` (single source of truth for Python and for emitted browser constants).

---

## Requirements

- **Python** ≥ 3.14  
- **[uv](https://docs.astral.sh/uv/)** for environments and commands  

---

## Install and test

```bash
uv sync
uv run pytest
```

Lint (optional, dev group):

```bash
uv run ruff check .
```

---

## Generated dashboard constants

The dashboard loads **`dashboard_constants.generated.js`** next to **`index.html`**. That file is **generated** from `canonical_library.py` by:

```bash
uv run python scripts/sync_dashboard_constants.py
```

Run this after changing token weights, colors, zone definitions, or `SCENARIO_LIBRARY` entries.

**CI:** GitHub Actions runs `pytest`, regenerates `dashboard_constants.generated.js`, then `git diff --exit-code dashboard_constants.generated.js` so the tracked file cannot drift from `canonical_library.py`.

Do **not** hand-edit `dashboard_constants.generated.js`.

---

## Running the surfaces

| Surface | Command / action |
|--------|-------------------|
| **Browser dashboard** | Open `index.html` in a modern browser (Chrome/Edge 111+, Firefox 113+, Safari 16.2+ for `color-mix()`). No server required. |
| **API** | `uv run uvicorn api:app --host 0.0.0.0 --port 8000` |
| **CLI** | `uv run python main.py relief` — also `not`, `moony`, `compare`, `wikidex`, `tui`, `dashboard`, etc. |
| **Batch client** | With the API up: `uv run python client.py` (optional base URL argument). |

Optional API auth: set env `TOKEN_CALC_API_KEY` and send header `X-API-Key`.

---

## HTTP `/compute` contract (summary)

- **`zone`**: one of `buildup`, `silence`, `drop`. For API requests, **`zone` is authoritative** — the engine does not overwrite it from `params["step"]` (step→zone sync remains the default for interactive calculator use when `sync_zone_from_step` is true).
- **`active_tokens`**: runtime slugs registered in `TOKEN_WEIGHTS` / `canonical_library.py` (e.g. `transistor`, `decorated`, `gate-on`, `bio-signal`, `freedom-signal`, …).
- **`operator_state`** (optional): trajectory / annotation modes enforced by the API — **`INTENTIONAL`**, **`BLACK`**, **`SSSEVERUS`**, **`LILY`**, **`PHOENIX`**, **`MAP`**. Defined in `contracts.py` for reuse by `client.py`.

Full behavior and persistence shapes: **`DESIGN.md`**, **`AGENTS.md`**, **`ROUTINE.md`**.

---

## Repository layout

| Path | Role |
|------|------|
| `index.html` | Standalone browser dashboard |
| `dashboard_constants.generated.js` | Generated from `canonical_library.py` (committed; sync via script) |
| `canonical_library.py` | Token colors/weights/labels, zones, `SCENARIO_LIBRARY` |
| `calculator.py` | Core compute engine |
| `design.py` | Dataclasses and domain helpers |
| `api.py` | FastAPI app (`/compute`, `/compare`, `/search`, `/health`, `/scenarios/moony`, …) |
| `client.py` | Batch client: 50 scenarios → `POST /compute` |
| `storage.py` | SQLite `compute_requests` trajectory |
| `scenarios.py` | Shared presets for CLI/API |
| `main.py` | CLI entry |
| `scripts/sync_dashboard_constants.py` | Emits `dashboard_constants.generated.js` |
| `contracts.py` | Shared API literals (e.g. `operator_state` set) |
| `tests/` | Pytest suite + HTML smoke check |

Other artifacts: `DESIGN.md`, `AUTHOR.md`, `AZKABAN.html`, `marauders_map.py`, `wikidex.py`, …

---

## Zones (behavior)

| Zone | Typical steps (reference) | Multiplier |
|------|---------------------------|------------|
| **buildup** | 0–43 | uses `intensity` parameter |
| **silence** | 44–47 | 0.0 — no signal strength |
| **drop** | 48–67 | 1.0 |

Step ranges describe the **interactive** model; API callers should set **`zone`** explicitly.

---

## Tokens (runtime vs label)

Runtime keys are lowercase slugs (e.g. `decorated`, `gate-on`). Display names come from `TOKEN_LABELS` in **`canonical_library.py`** (e.g. `DECORATED_VAR`, `GATE·ARMED`). The dashboard cards highlight the core seven-type harness; the Python/API surface includes additional canonical tokens (dark-mark roster, protection tokens, etc.) per that module.

---

## License

Apache License 2.0 — see [LICENSE](LICENSE).

---

## Version

**1.0.0** — evolved through 2026; see `CHANGELOG.md` for notable changes.
