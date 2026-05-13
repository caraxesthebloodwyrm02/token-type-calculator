---
name: scenario-runner
description: "Run a named token-type-calculator scenario via the CLI or API and interpret the output. Use when: running a scenario, testing a fingerprint, checking gate state, verifying no-take boundary, comparing outputs."
---

# Scenario Runner

Run a named scenario and interpret the result.

## Available scenario verbs (CLI)

| Verb | What it exercises |
|------|------------------|
| `relief` | TRANSISTOR-dominant, gate ARMED path |
| `not` | GATE_OFF token, UNARMED gate state |
| `moony` | MOONY fingerprint + bio-signal integration |
| `compare` | Side-by-side fingerprint similarity report |
| `wikidex` | Classify artifacts into 9 cognition patterns |
| `tui` | Full Rich TUI display |
| `dashboard` | Open browser dashboard |

## Run a scenario

```bash
cd /home/irfankabir/lab/token-type-calculator
uv run python main.py ${input:scenario:relief}
```

## Interpret output

Key fields to check:
- `dominant_token` — highest-weight token present
- `gate_state` — ARMED / UNARMED / N/A
- `is_no_take` — True if `engagement_cost > 0` and `service_value == 0`
- `is_anomaly` — should match `is_no_take` on boundary triggers
- `signal_strength` — 0.0 in Silence zone (steps 44–47), regardless of tokens
- `fingerprint_match` — name of closest canonical scenario (one of 14)

## Run all scenarios via batch client (requires API server)

```bash
# Terminal 1
uv run uvicorn api:app --host 0.0.0.0 --port 8000

# Terminal 2
uv run python client.py
```

Client posts 50 scenarios and prints a NO-TAKE summary table.
