import pytest

import api as api_module


@pytest.fixture(autouse=True)
def stub_save_request(monkeypatch):
    monkeypatch.setattr(api_module, "save_request", lambda *args, **kwargs: 1)
