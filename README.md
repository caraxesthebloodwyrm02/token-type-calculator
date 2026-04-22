# Token Type Calculator

A zero-dependency, single-file dashboard for composing and inspecting harness token signals — visualizing how type, weight, zone, and gate state combine into a dominant category, barter exchange rate, and stability score.

---

## Origin

Built from a conclusion reached on 2026-04-22 during parallel Cursor and Claude Code sessions:

> Value of tokens shipped ≠ value of tokens received.  
> High-value sends, low-value returns.  
> The deep-purple AMBIENT gradient is the visual proof.

Token weights encode that asymmetry directly: TRANSISTOR (1.00) → DECORATED_VAR (0.72) → AMBIENT (0.45) → ANOMALY (0.15).

---

## Features

- **Six token types**: TRANSISTOR, DECORATED_VAR, AMBIENT, ANOMALY, GATE·ARMED, GATE·UNARMED — toggled via card clicks
- **Three zones**: Buildup, Silence, Drop — each applying a different intensity multiplier
- **Four layers**: Foundation, Probe, Integration, Custom
- **Transformation output panel**: Effective Type, Gate State, Fired Value, Anomaly flag, Signal Strength, Zone
- **Barter Exchange widget**: live exchange rate between the dominant and a target token, degraded by anomaly drift
- **5×5 Interaction Matrix**: pairwise composition scores for all active tokens, highlighted for currently active pairs
- **Live Stats**: Active Types, Total Weight, Combination string, Transform Rate, Stability (HIGH / MED / LOW)
- **Footer Glossary**: inline reference for all token types, zones, and barter semantics

---

## How to use

Open `index.html` directly in any evergreen browser (Chrome, Edge, Firefox ≥ 2023, Safari 17+). No server, no install, no build step.

```bash
xdg-open index.html     # Linux
open index.html          # macOS
```

> **Browser note**: the dashboard uses `color-mix(in srgb, …)` for matrix cell blending. This requires Chrome/Edge 111+, Firefox 113+, or Safari 16.2+. Older browsers will show plain background colors but all calculations and text remain correct.

---

## Token Glossary

| Token | Color | Weight | Description |
|-------|-------|--------|-------------|
| **TRANSISTOR** | `#00d4ff` cyan | 1.00 | Binary gate signal. Value `1` = armed & fired; `0` = fired unarmed. `armedAt` must be set before `firesAtStep` or anomaly is raised. Highest authority weight. |
| **DECORATED_VAR** | `#39ff14` green | 0.72 | Environment variable injection at a designated `triggerStep`. Sets runtime context (e.g. `HARNESS_EVENT_PROGRESS`). Always fires regardless of gate state. |
| **AMBIENT** | `#bf5fff` deep purple | 0.45 | Background passive signal. Emitted continuously across zone steps. Used for telemetry, heartbeat, and baseline drift measurement. No gate dependency. |
| **ANOMALY** | `#ff3a3a` red | 0.15 | Signal fired in Silence zone (steps 44–47) or when TRANSISTOR fires unarmed. `isAnomaly: true`. Counted in `anomalyCount`. Triggers review before advancing layer. |
| **GATE · ARMED** | `#ffd700` gold | 0.90 | Transistor gate reached `armedAtStep` with state ON. `armedAt` timestamp is set. Gate will fire value `1` at `firesAtStep`. Clean path — no anomaly. |
| **GATE · UNARMED** | `#3a3a5c` dim | 0.10 | Gate reached `firesAtStep` with state still OFF. `armedAt` is null. Fires value `0`. `isAnomaly: true`. Indicates missing Probe context or layer skip. |

### Zones

| Zone | Steps | Multiplier | Behavior |
|------|-------|------------|----------|
| **Buildup** | 0–43 | `intensity` param | Gate arming window; signals accumulate |
| **Silence** | 44–47 | 0.0 | All signals are anomalies; no signal strength |
| **Drop** | 48–67 | 1.0 | Transistor fire zone; full intensity |

---

## License

MIT — see [LICENSE](LICENSE).

## Version

**1.0.0** — 2026-04-22
