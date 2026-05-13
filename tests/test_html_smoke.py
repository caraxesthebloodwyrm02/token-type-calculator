import pytest
from pathlib import Path


def test_html_smoke():
    """Verify index.html has required structural elements.

    index.html is tracked in git. If it was deleted from the working tree,
    this test fails to alert that the static dashboard is missing.

    dashboard_constants.generated.js is emitted from canonical_library.py via
    scripts/sync_dashboard_constants.py and must be present alongside index.html.
    """
    root = Path(__file__).parent.parent
    html_path = root / "index.html"
    gen_path = root / "dashboard_constants.generated.js"
    assert html_path.exists(), f"index.html not found at {html_path} — may be staged deleted"
    assert gen_path.exists(), (
        f"missing {gen_path.name} — run: uv run python scripts/sync_dashboard_constants.py"
    )
    html = html_path.read_text()

    assert html.startswith("<!DOCTYPE html>"), "Missing DOCTYPE"
    assert "<title>Token Type Calculator</title>" in html, "Missing title"
    assert "<body" in html, "Missing body element"
    assert "transistor" in html and "decorated" in html, "Missing token types"
    assert "dashboard_constants.generated.js" in html, "index.html must load generated dashboard constants"