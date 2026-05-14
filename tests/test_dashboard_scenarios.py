"""End-to-end browser drive of the three ROUTINE Day 1 scenarios.

Loads index.html via file:// in headless Chromium, exercises the real DOM
event handlers (token toggles, sliders, zone buttons), and reads the rendered
output panel — the same code path a team member hits when opening the Pages URL.

Requires playwright + a chromium install. CI skips this file via the import-skip
below until the runner has chromium provisioned; locally run after:

    uv sync --all-groups && uv run playwright install chromium
"""

from pathlib import Path
from typing import Any

import pytest

pw_api = pytest.importorskip("playwright.sync_api")
sync_playwright = pw_api.sync_playwright
TimeoutError = pw_api.TimeoutError

INDEX_HTML = (Path(__file__).parent.parent / "index.html").resolve()
FILE_URL = INDEX_HTML.as_uri()


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(headless=True)
        except Exception as exc:
            pytest.skip(f"chromium unavailable: {exc}")
        yield b
        b.close()


@pytest.fixture
def page(browser):
    page = browser.new_page()
    page.goto(FILE_URL)
    page.wait_for_selector(".token-card.active", timeout=5000)
    yield page
    page.close()


def set_active_tokens(page, target: set[str]) -> None:
    """Sync active tokens to exactly `target`. Adds before removing so the set
    never collapses to zero (toggleToken refuses to remove the last one)."""
    current = set(
        page.eval_on_selector_all(
            ".token-card.active", "els => els.map(e => e.dataset.type)"
        )
    )
    for t in target - current:
        page.click(f'.token-card[data-type="{t}"]')
    for t in current - target:
        page.click(f'.token-card[data-type="{t}"]')


def set_slider(page, slug: str, value_0_to_1: float) -> None:
    """Set a 0-1 parameter slider. Range inputs are 0-100; the page divides by 100."""
    raw = int(round(value_0_to_1 * 100))
    page.evaluate(
        """([slug, raw]) => {
            const el = document.getElementById('s-' + slug);
            el.value = String(raw);
            el.dispatchEvent(new Event('input', { bubbles: true }));
        }""",
        [slug, raw],
    )


def set_zone(page, zone: str) -> None:
    page.click(f'.zone-btn[data-zone="{zone}"]')


def read_outputs(page) -> dict[str, Any]:
    return page.evaluate(
        """() => ({
            type:     document.getElementById('out-type').textContent,
            gate:     document.getElementById('out-gate').textContent,
            value:    document.getElementById('out-value').textContent,
            anomaly:  document.getElementById('out-anomaly').textContent,
            boundary: document.getElementById('out-boundary').textContent,
            movement: document.getElementById('out-movement').textContent,
            strength: document.getElementById('out-strength').textContent,
            zone:     document.getElementById('out-zone').textContent,
        })"""
    )


def test_scenario_moony(page):
    """S1 — bio-signal only, cost 1.0 / value 0.0, buildup. Canonical NO-TAKE."""
    set_active_tokens(page, {"bio-signal"})
    set_zone(page, "buildup")
    set_slider(page, "engagement_cost", 1.0)
    set_slider(page, "service_value", 0.0)

    out = read_outputs(page)
    assert out["type"] == "BIO_SIGNAL", out
    assert out["boundary"] == "NO-TAKE (NOT)", out
    assert out["gate"] == "N/A", out
    assert out["anomaly"] == "TRUE", out
    assert out["movement"] == "TURBULENT", out
    assert out["zone"] == "BUILDUP", out


def test_scenario_gate_on_clean_drop(page):
    """S2 — transistor + gate-on, cost 0.5 / value 0.8, drop. Clean armed firing."""
    set_active_tokens(page, {"transistor", "gate-on"})
    set_zone(page, "drop")
    set_slider(page, "engagement_cost", 0.5)
    set_slider(page, "service_value", 0.8)

    out = read_outputs(page)
    assert out["type"] == "TRANSISTOR", out
    assert out["boundary"] == "OPEN", out
    assert out["gate"] == "ARMED", out
    assert out["value"] == "1", out
    assert out["anomaly"] == "FALSE", out
    assert out["movement"] == "DRIFT", out
    assert out["zone"] == "DROP", out
    assert float(out["strength"]) > 0.0


def test_scenario_unarmed_no_take(page):
    """S3 — transistor + gate-off, cost 1.0 / value 0.0, buildup. Unarmed NO-TAKE."""
    set_active_tokens(page, {"transistor", "gate-off"})
    set_zone(page, "buildup")
    set_slider(page, "engagement_cost", 1.0)
    set_slider(page, "service_value", 0.0)

    out = read_outputs(page)
    assert out["type"] == "TRANSISTOR", out
    assert out["boundary"] == "NO-TAKE (NOT)", out
    assert out["gate"] == "UNARMED", out
    assert out["value"] == "0", out
    assert out["anomaly"] == "TRUE", out
    assert out["movement"] == "TURBULENT", out
    assert out["zone"] == "BUILDUP", out
