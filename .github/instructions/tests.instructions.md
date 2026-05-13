---
applyTo: "tests/**/*.py,test_*.py"
---

# Test conventions — token-type-calculator

## Ephemeral DB
Always use `tmp_path` fixture for SQLite tests. Never touch `token_calc.db` in tests.

```python
def test_example(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(str(db_path))
```

## HTTP mocking
Mock HTTP responses via the `_mock_response` helper defined in `test_client.py`. Do not use real network calls.

## Coverage targets
- `test_calculator.py` — boundary rejection, gate states (ARMED/UNARMED/N/A), bio-signal integration, silence zone (steps 44–47 must yield strength = 0).
- `test_storage.py` — `init_db` idempotency, `save_request` / `read_trajectory` round-trip, `active_tokens` sorted on write.
- `test_client.py` — exactly 50 scenarios generated, exactly 15 no-take in canonical set, 400 / 500 / `ConnectionError` handled gracefully.

## No-take assertion pattern
```python
assert result.is_no_take is True
assert result.is_anomaly is True
```
Both flags must be set when `engagement_cost > 0` and `service_value == 0`.

## Run command
```bash
uv run pytest
```
No custom marks. No conftest.py at root — fixtures are inline.
