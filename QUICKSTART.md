# QUICKSTART

The Token Type Calculator is a small dashboard. You give it a few inputs about an exchange — which tokens are active, how much you put in, how much you got back — and it returns a one-glance picture of how that exchange landed: dominant type, whether the boundary held, where it sits on a buildup → silence → drop arc, and how stable the signal is.

You do not need to install anything to use it.

---

## Open it

**On the web:** <https://caraxesthebloodwyrm02.github.io/token-type-calculator/>

**Locally (if the link is not up yet):** clone the repo and open `index.html` in a recent browser (Chrome 111+, Firefox 113+, Safari 16.2+). No server, no install, no terminal.

---

## The three controls

The dashboard has more than three controls, but these are the ones you need to understand to get value out of it.

### 1. Token toggles

A row of named tokens — `TRANSISTOR`, `DECORATED`, `AMBIENT`, `GATE·ARMED`, `GATE·UNARMED`, `BIO_SIGNAL`, and a few others. Click each to turn it on or off. At least one must be on.

The set of active tokens is the single most important input. It decides which "type" the exchange is read as, and which gates are available.

### 2. Engagement Cost and Service Value

Two numbers, each between 0 and 1.

- **Engagement Cost** — how much you paid into the exchange (attention, time, body).
- **Service Value** — how much you got back.

When cost is high and value is zero, the calculator returns **NO-TAKE**. That is a deliberate boundary, not a bug — the calculator's central rule is that an exchange with cost and no service is refused.

### 3. Step

A number from 0 to 67. It places the exchange on the arc:

| Range | Zone |
|-------|------|
| 0–43  | buildup |
| 44–47 | silence |
| 48–67 | drop |

Most of the time the default is fine. Change it when you want to ask "what would this same exchange look like in the drop?"

---

## A 30-second worked example

1. Open the dashboard.
2. Toggle on **BIO_SIGNAL**. Turn the others off.
3. Set **Engagement Cost** to `1.0`. Set **Service Value** to `0.0`.
4. Read the **Boundary** field: it should say `NO-TAKE`.
5. Now move **Service Value** to `1.0`. Read it again: `OPEN`.

You just walked the calculator across its single most important rule. Every other feature builds on this.

---

## What the panels mean

- **Transformation Output** — the headline. Dominant token, gate state, fired value, boundary status, signal strength, zone.
- **Live Stats** — the secondary numbers. Stability, transform rate, total weight, the costs you set.
- **Air Element** — a qualitative reading. Movement (drift / gust / turbulent / still), pressure, clarity.
- **Audio Signal** — voice-spec output, if you're routing the result into a downstream system.

---

## What the web dashboard does *not* do

The deployed page is stateless. It does not save your history, it does not run the named operator-state views (`INTENTIONAL`, `BLACK`, `PHOENIX`, and friends), and it does not draw the trajectory map. Those features live in the Python API and CLI; the web link is the calculator only.

If you want history or operator-state views, run the API locally — instructions in [README.md](README.md).

---

## Where to go next

- **Stuck on a control?** Reply on the share thread, or ping the project owner.
- **Curious about the named scenarios** (`MOONY`, `TONKS`, `PRONGS`, …)? Those are private vocabulary from the project's origin. They are interesting but optional — the calculator works without ever learning a single one. Long version under `docs/lore/`.
- **Building on this?** Start with [DESIGN.md](DESIGN.md) and [AGENTS.md](AGENTS.md).
