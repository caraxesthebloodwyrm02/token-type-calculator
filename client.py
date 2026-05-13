"""Standalone client for the token type calculator API.

Day 4 of ROUTINE.md: making the calls. Posts a batch of 50 generated scenarios
to /compute, persists what comes back (the API handles storage), and prints a
"NO-TAKE events counted" summary report.

See AUTHOR.md for the contract:
  - build_scenarios() returns exactly 50 scenarios.
  - Of those, exactly 15 are canonical no-take (cost=1.0, value=0.0).
  - post_compute returns dict on 200, None on 400/500, sys.exit(1) on
    ConnectionError. The API not being reachable is an operator-level failure;
    a single bad payload is not.
  - run_batch posts every scenario and drops Nones before returning.
"""

import sys
from collections import Counter
from typing import Any, Optional

import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

DEFAULT_BASE_URL = "http://localhost:8000"
COMPUTE_PATH = "/compute"
REQUEST_TIMEOUT_SECONDS = 10.0


# ---------------------------------------------------------------------------
# Scenario generation
# ---------------------------------------------------------------------------


def _scenario(
    active_tokens: list[str],
    zone: str,
    intensity: float,
    momentum: float,
    score: float,
    drift: float,
    engagement_cost: float,
    service_value: float,
    operator_state: Optional[str] = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "active_tokens": active_tokens,
        "zone": zone,
        "intensity": intensity,
        "momentum": momentum,
        "score": score,
        "drift": drift,
        "engagement_cost": engagement_cost,
        "service_value": service_value,
    }
    if operator_state is not None:
        payload["operator_state"] = operator_state
    return payload


def build_scenarios() -> list[dict[str, Any]]:
    """Return 50 scenarios spanning the exchange space.

    Mix:
      - 15 canonical NO-TAKE (cost=1.0, value=0.0) — varying token sets / zones
      - 15 RELIEF (cost>0 AND value>=cost) — clean exchanges
      - 10 OPEN-borderline (cost low, value low — boundary should stay open)
      - 5 SILENCE-zone anomalies (zone='silence' — strength forced to 0)
      - 5 operator-state probes (INTENTIONAL / BLACK / MAP) — exercises api.py
        branches without changing the shape returned to run_batch.
    Total = 50.
    """
    scenarios: list[dict[str, Any]] = []

    # --- 15 NO-TAKE: cost paid, service absent --------------------------
    no_take_tokens = [
        ["bio-signal"],
        ["bio-signal", "anomaly"],
        ["bio-signal", "transistor"],
        ["bio-signal", "gate-off"],
        ["bio-signal", "ambient"],
        ["anomaly"],
        ["anomaly", "ambient"],
        ["anomaly", "decorated"],
        ["bio-signal", "anomaly", "gate-off"],
        ["decorated", "anomaly"],
        ["ambient", "anomaly"],
        ["transistor", "gate-off"],
        ["bio-signal", "decorated", "anomaly"],
        ["bio-signal", "ambient", "anomaly"],
        ["bio-signal", "transistor", "anomaly"],
    ]
    for i, tokens in enumerate(no_take_tokens):
        scenarios.append(_scenario(
            active_tokens=tokens,
            zone="buildup" if i % 2 == 0 else "silence",
            intensity=0.5 + (i % 5) * 0.1,
            momentum=1.0,
            score=0.5 + (i % 3) * 0.15,
            drift=0.1 + (i % 4) * 0.05,
            engagement_cost=1.0,
            service_value=0.0,
        ))

    # --- 15 RELIEF: cost paid, service delivered ------------------------
    relief_tokens = [
        ["transistor", "gate-on"],
        ["transistor", "gate-on", "decorated"],
        ["transistor", "gate-on", "ambient"],
        ["decorated", "gate-on"],
        ["transistor", "decorated", "gate-on"],
        ["transistor", "gate-on", "bio-signal"],
        ["gate-on", "ambient"],
        ["transistor", "ambient"],
        ["decorated", "ambient"],
        ["transistor", "gate-on", "decorated", "ambient"],
        ["transistor", "decorated"],
        ["gate-on", "bio-signal"],
        ["transistor", "bio-signal", "gate-on"],
        ["decorated", "gate-on", "ambient"],
        ["transistor", "gate-on", "decorated", "bio-signal"],
    ]
    for i, tokens in enumerate(relief_tokens):
        cost = 0.4 + (i % 4) * 0.15
        scenarios.append(_scenario(
            active_tokens=tokens,
            zone="drop" if i % 3 == 0 else "buildup",
            intensity=0.6 + (i % 5) * 0.08,
            momentum=0.9 + (i % 3) * 0.05,
            score=0.7 + (i % 4) * 0.07,
            drift=0.05 + (i % 5) * 0.03,
            engagement_cost=round(cost, 2),
            service_value=round(cost + 0.2 + (i % 3) * 0.1, 2),
        ))

    # --- 10 OPEN-borderline: low cost, low value, boundary stays OPEN ---
    borderline_tokens = [
        ["transistor"],
        ["transistor", "ambient"],
        ["ambient"],
        ["transistor", "decorated"],
        ["decorated"],
        ["transistor", "bio-signal"],
        ["ambient", "decorated"],
        ["transistor", "gate-on"],
        ["bio-signal", "ambient"],
        ["transistor", "ambient", "decorated"],
    ]
    for i, tokens in enumerate(borderline_tokens):
        scenarios.append(_scenario(
            active_tokens=tokens,
            zone="buildup",
            intensity=0.3 + (i % 4) * 0.1,
            momentum=0.8,
            score=0.6 + (i % 3) * 0.1,
            drift=0.08,
            engagement_cost=0.0,
            service_value=0.0,
        ))

    # --- 5 SILENCE-zone anomalies --------------------------------------
    silence_tokens = [
        ["transistor"],
        ["transistor", "ambient"],
        ["decorated", "ambient"],
        ["transistor", "decorated"],
        ["bio-signal", "transistor"],
    ]
    for i, tokens in enumerate(silence_tokens):
        scenarios.append(_scenario(
            active_tokens=tokens,
            zone="silence",
            intensity=0.5,
            momentum=1.0,
            score=0.7,
            drift=0.1 + i * 0.05,
            engagement_cost=0.2,
            service_value=0.3,
        ))

    # --- 5 operator-state probes ---------------------------------------
    # Note: probes deliberately avoid (cost=1.0, value=0.0) so they don't
    # double-count against the 15 NO-TAKE scenarios above. The BLACK probe
    # uses cost=0.9 to stay close to the boundary without crossing it.
    probes = [
        ("INTENTIONAL", ["transistor", "gate-on"], "buildup", 0.3, 0.8),
        ("BLACK", ["bio-signal", "anomaly"], "silence", 0.9, 0.0),
        ("BLACK", ["transistor", "gate-on", "bio-signal"], "drop", 0.6, 0.9),
        ("MAP", ["transistor", "ambient", "decorated"], "buildup", 0.4, 0.5),
        ("INTENTIONAL", ["bio-signal", "transistor"], "drop", 0.5, 0.7),
    ]
    for state, tokens, zone, cost, value in probes:
        scenarios.append(_scenario(
            active_tokens=tokens,
            zone=zone,
            intensity=0.7,
            momentum=1.0,
            score=0.8,
            drift=0.1,
            engagement_cost=cost,
            service_value=value,
            operator_state=state,
        ))

    assert len(scenarios) == 50, f"expected 50 scenarios, got {len(scenarios)}"
    return scenarios


# ---------------------------------------------------------------------------
# Transport
# ---------------------------------------------------------------------------

def post_compute(
    payload: dict[str, Any],
    base_url: str = DEFAULT_BASE_URL,
) -> Optional[dict[str, Any]]:
    """POST one scenario to /compute.

    Returns the parsed JSON on HTTP 200.
    Returns None on HTTP 400 or 500 — bad input is data, not a crash.
    Calls sys.exit(1) on requests.ConnectionError — if the API is unreachable
      there is nothing for the rest of the batch to do.
    """
    url = f"{base_url.rstrip('/')}{COMPUTE_PATH}"
    try:
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        sys.stderr.write(
            f"client: cannot reach API at {url} — is uvicorn running?\n"
        )
        sys.exit(1)

    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            return None

    if response.status_code in (400, 500):
        # Surface the failure for the operator but do not raise.
        try:
            detail = response.json()
        except ValueError:
            detail = response.text
        sys.stderr.write(
            f"client: {response.status_code} from /compute — {detail!r}\n"
        )
        return None

    # Unexpected status — treat like a soft failure so the batch keeps moving.
    sys.stderr.write(
        f"client: unexpected status {response.status_code} from /compute\n"
    )
    return None


# ---------------------------------------------------------------------------
# Batch + summary
# ---------------------------------------------------------------------------

def run_batch(base_url: str = DEFAULT_BASE_URL) -> list[dict[str, Any]]:
    """Post every scenario from build_scenarios() and return the successful results."""
    results: list[dict[str, Any]] = []
    for payload in build_scenarios():
        result = post_compute(payload, base_url=base_url)
        if result is not None:
            results.append(result)
    return results


def summarize(results: list[dict[str, Any]]) -> None:
    """Day 4 "NO-TAKE events counted" report. Rich-formatted."""
    console = Console()

    if not results:
        console.print(Panel(Text("No successful results to summarize.", style="bold red")))
        return

    total = len(results)
    no_take = sum(1 for r in results if r.get("is_no_take"))
    open_count = total - no_take
    anomalies = sum(1 for r in results if r.get("is_anomaly"))

    boundary_counter: Counter[str] = Counter(
        (r.get("boundary_status") or "UNKNOWN") for r in results
    )
    stability_counter: Counter[str] = Counter(
        (r.get("stability") or "UNKNOWN") for r in results
    )
    dominant_counter: Counter[str] = Counter(
        (r.get("dominant") or "unknown") for r in results
    )

    console.print(Panel(Text("BATCH REPORT — TOKEN TYPE CALCULATOR", justify="center", style="bold cyan")))

    headline = Table.grid(padding=(0, 2))
    headline.add_column(style="dim")
    headline.add_column(style="bold")
    headline.add_row("Total received", str(total))
    headline.add_row("NO-TAKE events", f"[#ff3a3a]{no_take}[/]")
    headline.add_row("OPEN events", f"[#39ff14]{open_count}[/]")
    headline.add_row("Anomalies", f"[#ffd700]{anomalies}[/]")
    console.print(Panel(headline, title="Headline", border_style="dim"))

    def _kv_table(title: str, counter: Counter[str]) -> Table:
        t = Table(title=title, show_header=True, header_style="bold")
        t.add_column("Key")
        t.add_column("Count", justify="right")
        for key, count in counter.most_common():
            t.add_row(str(key), str(count))
        return t

    console.print(_kv_table("Boundary status", boundary_counter))
    console.print(_kv_table("Stability", stability_counter))
    console.print(_kv_table("Dominant token", dominant_counter))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: Optional[list[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    base_url = DEFAULT_BASE_URL
    if argv:
        # Single optional positional arg: base URL override.
        base_url = argv[0]

    results = run_batch(base_url=base_url)
    summarize(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
