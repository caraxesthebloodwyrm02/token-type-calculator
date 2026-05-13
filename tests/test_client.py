import sys
from unittest.mock import MagicMock, patch

import pytest
import requests

sys.path.insert(0, ".")

from client import build_scenarios, post_compute, run_batch


def _mock_response(status_code: int, json_body: dict | None = None) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_body or {}
    return mock


def test_build_scenarios_count():
    assert len(build_scenarios()) == 50


def test_build_scenarios_no_take_count():
    no_take = [
        s for s in build_scenarios()
        if s["engagement_cost"] == 1.0 and s["service_value"] == 0.0
    ]
    assert len(no_take) == 15


def test_post_compute_handles_400():
    with patch("requests.post", return_value=_mock_response(400, {"detail": "bad input"})):
        result = post_compute({"active_tokens": ["transistor"], "zone": "buildup"})
    assert result is None


def test_post_compute_handles_500():
    with patch("requests.post", return_value=_mock_response(500)):
        result = post_compute({"active_tokens": ["transistor"], "zone": "buildup"})
    assert result is None


def test_post_compute_handles_connection_error():
    with patch("requests.post", side_effect=requests.ConnectionError):
        with pytest.raises(SystemExit) as exc_info:
            post_compute({"active_tokens": ["transistor"], "zone": "buildup"})
    assert exc_info.value.code == 1


def test_run_batch_filters_none():
    valid_result = {"boundary_status": "OPEN", "strength": 0.5}
    call_count = 0

    def mock_post_compute(payload, base_url="http://localhost:8000"):
        nonlocal call_count
        call_count += 1
        return None if call_count <= 5 else valid_result

    with patch("client.post_compute", side_effect=mock_post_compute):
        results = run_batch()

    assert len(results) == 45
