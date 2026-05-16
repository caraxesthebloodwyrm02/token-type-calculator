"""Direct-call tests for /compare, /search, and /scenarios/moony routes.

Same pattern as test_api_contract.py: call the FastAPI handler directly,
stub save_request to avoid touching SQLite.
"""

import pytest

import api as api_module
from api import (
    CompareRequest,
    ComputeRequest,
    compare,
    moony_scenario,
    search,
)


@pytest.fixture(autouse=True)
def stub_save_request(monkeypatch):
    monkeypatch.setattr(api_module, "save_request", lambda *args, **kwargs: 1)


class TestCompare:
    def test_compare_returns_two_states_and_report(self):
        result = compare(CompareRequest(
            a=ComputeRequest(active_tokens=["transistor"], zone="buildup"),
            b=ComputeRequest(active_tokens=["bio-signal"], zone="silence", engagement_cost=1.0, service_value=0.0),
        ))
        assert "a" in result and "b" in result and "report" in result
        assert result["a"]["dominant"] != result["b"]["dominant"] or result["a"]["zone"] != result["b"]["zone"]

    def test_compare_report_has_similarity(self):
        result = compare(CompareRequest(
            a=ComputeRequest(active_tokens=["transistor"], zone="buildup"),
            b=ComputeRequest(active_tokens=["transistor"], zone="buildup"),
        ))
        report = result["report"]
        assert hasattr(report, "similarity")
        assert 0.0 <= report.similarity <= 1.0

    def test_compare_identical_states_high_similarity(self):
        req = ComputeRequest(active_tokens=["transistor"], zone="buildup")
        result = compare(CompareRequest(a=req, b=req))
        assert result["report"].similarity >= 0.9

    def test_compare_both_sides_have_story(self):
        result = compare(CompareRequest(
            a=ComputeRequest(active_tokens=["transistor"], zone="buildup"),
            b=ComputeRequest(active_tokens=["transistor"], zone="drop", intensity=1.0),
        ))
        assert isinstance(result["a"]["story"], str)
        assert isinstance(result["b"]["story"], str)


class TestSearch:
    def test_search_returns_closest_scenario(self):
        result = search(ComputeRequest(active_tokens=["transistor"], zone="buildup"))
        assert "closest_scenario" in result
        assert isinstance(result["closest_scenario"], str)

    def test_search_returns_report(self):
        result = search(ComputeRequest(active_tokens=["transistor"], zone="buildup"))
        assert hasattr(result["report"], "similarity")

    def test_search_returns_query_result(self):
        result = search(ComputeRequest(active_tokens=["transistor"], zone="buildup"))
        assert "query_result" in result
        assert "dominant" in result["query_result"]


class TestMoonyScenario:
    def test_moony_returns_compute_response(self):
        result = moony_scenario()
        assert "dominant" in result
        assert "fingerprint" in result
        assert "story" in result

    def test_moony_is_anomaly(self):
        result = moony_scenario()
        assert result["is_anomaly"] is True

    def test_moony_dominant_is_bio_signal(self):
        result = moony_scenario()
        assert result["dominant"] == "bio-signal"
