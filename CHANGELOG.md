# Changelog

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-05-16

### Added
- FastAPI backend (`api.py`) with `/compute`, `/compare`, `/search`, `/scenarios/moony`, `/health` endpoints
- SQLite trajectory storage (`storage.py`) with `save_request` / `read_trajectory`
- Batch HTTP client (`client.py`) with 50-scenario composition library
- Rich CLI (`main.py`) and TUI anchor (4 canonical prompts)
- `TokenTypeCalculator.compute()` — full signal pipeline with gate state, fingerprint, air element, NO-TAKE boundary
- `TokenTypeCalculator.calculate_similarity()` and `semantic_search()` — fingerprint A/B comparison and closest-scenario search
- Dark Mark system: `is_dark_mark_cast`, `check_dark_mark`, `check_imperius_compromise` — module-level gates, never embedded in weight arithmetic
- Expecto Patronum: `expecto_patronum` at the `(engagement=1.0, service=1.0)` coordinate opposite the Dark Mark
- Freedom signal override (`check_freedom_signal`) — Dobby's sock: paid cost asserts freedom, flips NO-TAKE
- Operator-state dispatch registry (`operator_states.py`): INTENTIONAL, BLACK, SSSEVERUS, LILY, PHOENIX, MAP
- Marauder's Map (`marauders_map.py`) with pack scores, Death Eater proximity, MORSMORDRE scope detection, REGULUS redemption arc, SIRIUS duality annotation
- Phase 2 character roster (8 new scenarios): VOLDEMORT, BELLATRIX, REGULUS, MCGONAGALL, SLUGHORN, SIRIUS_BLACK, KREACHER_RECLAIMED, DOBBY
- Dark-side tokens: `morsmordre`, `legilimens`, `imperius`, `protego`, `freedom-signal` in canonical library
- `canonical_library.py` — single source of truth for token weights, colors, and scenario fingerprints (Python and dashboard)
- `scripts/sync_dashboard_constants.py` — generates `dashboard_constants.generated.js` from canonical library
- Dynamic token grid in `index.html` — cards rendered from `TOKEN_WEIGHTS` / `TOKEN_COLORS`, no hardcoded HTML
- CI pipeline (GitHub Actions): pytest, constants drift check, ruff lint
- 105 tests across 12 test files covering calculator, API contract, operator_state branches, Dark Mark path, protection charms, marauders map, storage, client, and HTML smoke

### Changed
- Token grid in `index.html` migrated from hardcoded cards to JS-rendered from generated constants
- `v1.0.0` was a zero-dependency single-file HTML dashboard; `v2.0.0` is a full multi-module Python system with that dashboard as the frontend

## [1.0.0] - 2026-04-22

### Added
- Six interactive token type cards: TRANSISTOR, DECORATED_VAR, AMBIENT, ANOMALY, GATE·ARMED, GATE·UNARMED
- Three zone selectors (Buildup / Silence / Drop) with multiplier-based signal strength computation
- Four layer buttons (Foundation / Probe / Integration / Custom)
- Six range sliders: Intensity, Step Position, Momentum, Score, Cycle Index, Drift
- Composite composition bar showing weighted token proportions
- Transformation output panel: Effective Type, Gate State, Fired Value, Anomaly, Signal Strength, Zone
- Barter Exchange widget with live rate degraded by anomaly drift
- 5×5 Interaction Matrix for pairwise token composition scores
- Live Stats panel: Active Types, Total Weight, Combination, Transform Rate, Stability
- Footer Signal Glossary with full annotation for every token type, zone, and barter rate
- Zero-dependency, zero-build, single-file HTML artifact
