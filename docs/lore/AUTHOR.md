# AUTHOR.md

> *"The compiler is your first line of defense; the IDE is your navigator."*
> — `ROUTINE.md`, Day 1

This file is the operator's stance behind the code. It is not a changelog and it is
not a design contract — those live in `CHANGELOG.md` and `DESIGN.md`. This file says
**how the author thinks**, so any module added later (including `storage.py` and
`client.py`) can be written in the same hand.

---

## Who is writing this

Plural intent. A single operator at the keyboard, but the project deliberately
preserves more than one voice:

- The **engineer** — Software Design Document conventions, Pydantic schemas,
  testable refusal logic, `PYTHONPATH=.` rituals.
- The **designer** — Google `DESIGN.md` style, color tokens, do/don't guardrails,
  conservative visual readings.
- The **operator** — the one who watched the lights, walked through AZKABAN, and
  came back with `TUI` as an anchor. The one who signs `--TUI` and, sometimes,
  `-- Hermes`.

These three are not separate authors. They are the same person at three different
distances from the screen.

---

## The one rule the whole project enforces

```
engagement_cost > 0  AND  service_value == 0   ⇒  NO-TAKE (NOT)
```

That is the structural rule. Every other decision in this codebase exists to keep
that rule **explicit, testable, and explainable**.

When in doubt about whether a feature belongs here, ask:

> Does this make the no-take boundary easier to see, easier to test, or easier
> to refuse from?

If yes, write it. If no, don't.

---

## Voice & vocabulary

Use the project's vocabulary literally — these are not metaphors decorating
ordinary code; they are the **names of the things**:

| Word            | Means                                                                 |
|-----------------|-----------------------------------------------------------------------|
| `TRANSISTOR`    | clean carrier signal (weight 1.00)                                    |
| `BIO_SIGNAL`    | lived/physical cost registered as data (weight 0.85)                  |
| `GATE·ARMED` / `GATE·UNARMED` | permission state — armed fires `1`, unarmed fires `0` and raises anomaly |
| `AMBIENT`       | background continuous signal — the gravitational constant             |
| `ANOMALY`       | drift, contradiction, boundary stress                                 |
| `NOT()`         | the refusal — cost paid, service absent                               |
| `TUI`           | creator-memory anchor; query contract, not decoration                 |
| `Air Element`   | the medium (pressure / clarity / movement) every exchange travels through |
| `Fingerprint`   | quantized state used for similarity search                            |
| `Marauder pack` | `MOONY` + `TONKS` + `PRONGS` + `PADFOOT` + `WORMTAIL` — opens `BLACK` |
| `BLACK`         | query scope (not a scenario) — relational/ancestral lens              |

When you write code in this project, **use these names in comments and
docstrings**. They are not flavor — they map directly to entries in
`SCENARIO_LIBRARY` and `TOKEN_WEIGHTS`.

---

## Conventions the code already follows

These are observed, not invented, by reading the existing files:

1. **Synchronicity** — `index.html` (browser) and `calculator.py` (server) mirror
   the same formulas. Any new calculation must be added to both, or noted as
   server-only with a reason.
2. **Type hints everywhere.** Dataclasses for structured data
   (`design.py`). `Literal[...]` for enum-like fields. Pydantic `BaseModel`
   only at the API edge.
3. **Idempotent setup.** `init_db()` is safe to call twice. The lifespan handler
   calls it once. The CLI calls it once. Any new entry point should also call
   it on start without fear.
4. **Persist every compute.** Every `/compute`, `/compare`, `/search`,
   `/scenarios/moony`, and CLI scenario writes a row via `save_request(...)`.
   This is what makes `read_trajectory()` meaningful.
5. **Sorted `active_tokens` on persistence.** Insertion order does not matter
   semantically, so the storage layer sorts tokens before serializing them.
   This is asserted in `tests/test_storage.py::test_active_tokens_sorted`.
6. **Conservative on uncertainty.** If a value is unknown, keep it unknown
   (`I_DONT_KNOW`), do not invent. Same applies to OCR, canvas reading, and
   API responses: prefer `None` to a guess.
7. **The TUI anchor is read-only.** Four canonical prompts, four canonical
   answers, every time. Never modify `TUI_ANCHOR`.
8. **Anomaly is data.** It is not an exception path. `is_anomaly: True` is a
   normal, expected return value — it does not raise.
9. **Refusal is also data.** `NO-TAKE (NOT)` is a `boundary_status` string, not
   an `HTTPException`. The API still returns 200 OK with a body that says the
   exchange was refused.

---

## What a "good" new module looks like

Pattern observed across `calculator.py`, `api.py`, `main.py`, `design.py`:

- **Header comment is sparse.** No banner art. Maybe one line of intent.
- **Imports grouped:** stdlib → third-party → local.
- **Constants at the top.** Names in `SCREAMING_SNAKE_CASE`. Values that came
  from `DESIGN.md` should match `DESIGN.md` exactly.
- **One class per responsibility, when a class is justified.** Otherwise
  module-level functions. `TokenTypeCalculator` is a class because it holds
  mutable state (`active_tokens`, `params`); the storage layer is functions
  because it doesn't.
- **Return shapes are dicts of primitives** for anything that crosses a
  boundary (HTTP, DB, CLI). Dataclasses live in-process.
- **Tests come with the module.** Each new module gets a `tests/test_<name>.py`
  with at minimum: idempotency, happy path, one failure mode.

---

## How `storage.py` should behave

Read together with `tests/test_storage.py`:

- `init_db(db_path: str = "token_calc.db") -> None` — creates the
  `compute_requests` table if missing. Idempotent. Safe to call twice in a row.
- `save_request(endpoint: str, params: dict, result: dict, duration_ms: float,
   db_path: str = "token_calc.db") -> int` — returns the new row id.
- A row at minimum carries the columns asserted by tests: `id`,
  `is_no_take` (int 0/1), `boundary_status` (string), `active_tokens` (JSON
  array, **sorted**).
- A row should also carry enough surface signal for `read_trajectory` to
  produce a useful map without re-parsing the full result blob:
  `timestamp_utc`, `dominant`, `air_movement`, `air_pressure`, `air_clarity`,
  `strength`, `transform_rate`, `stability`.
- `read_trajectory(limit: int = 10, db_path: str = "token_calc.db") ->
   list[dict]` — most-recent-last, used by `marauders_map.py` and the
  `INTENTIONAL` / `BLACK` / `MAP` operator paths in `api.py`.
- Non-JSON-serializable dataclasses inside `result` (`Fingerprint`,
  `AudioSignal`, `Face`, `AirElement`) are normalized to dicts via
  `dataclasses.asdict` before storage.

---

## How `client.py` should behave

Read together with `tests/test_client.py` and `ROUTINE.md` Day 4:

- `build_scenarios() -> list[dict]` — returns exactly **50** scenarios.
  Of those, exactly **15** must be canonical no-take (`engagement_cost == 1.0`
  AND `service_value == 0.0`). The remaining 35 cover the open / relief
  shape of the exchange space (clean transistor fires, gate-armed, bio-signal
  with service value, ambient drift, etc.).
- `post_compute(payload: dict, base_url: str = "http://localhost:8000")
   -> dict | None` —
   - On HTTP 200, return parsed JSON.
   - On HTTP 400 or 500, return `None` (do not raise). The error is data.
   - On `requests.ConnectionError`, `sys.exit(1)` — the API not being
     reachable is an operator-level failure, not a per-call failure.
- `run_batch(base_url: str = "http://localhost:8000") -> list[dict]` —
  posts every scenario from `build_scenarios()`, drops `None` results,
  returns the surviving list. Test fixture relies on exactly this shape.
- `summarize(results: list[dict]) -> None` — Day 4 "NO-TAKE events
  counted" report. Uses Rich. Prints counts, the boundary breakdown, the
  stability distribution, and the most common dominant token.

Both modules use `requests` (already in `pyproject.toml`) and `rich` for any
human-readable output. No new top-level dependencies.

---

## Style notes

- Prefer `with sqlite3.connect(...) as conn:` over manual close.
- Prefer parameterized SQL (`?`) over f-strings. Always.
- Prefer `json.dumps(payload, default=_to_jsonable)` over reaching into
  individual dataclasses by name.
- Prefer `time.perf_counter()` for `duration_ms`, never `time.time()`.
- Prefer ISO-8601 UTC timestamps (`datetime.now(timezone.utc).isoformat()`)
  — `timestamp_utc` is the column name; the `_utc` suffix is load-bearing.
- Never print from inside a library module. Printing is the CLI's job.
  Exception: `client.py` is itself a CLI — it may print.

---

## What this project is actually about

The dashboard, the API, the database — these are scaffolding. What the project
is recording is **the difference between value sent and value received**, and
giving that difference a name (`NO-TAKE`) so it can be refused on contact
rather than absorbed and explained later.

`BIO_SIGNAL` exists because the body keeps the receipt even when the ledger
doesn't. `BLACK` exists because betrayal (`WORMTAIL`) only becomes legible in
the context of the guardian (`PADFOOT`) and the gravitational constant
(`PRONGS`). `TUI` exists because the operator wanted to remember where they
were standing when they started building this.

Write code that respects that. Don't make the boundary harder to see.

---

*-- TUI*

