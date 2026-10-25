import pytest

import api


class FakeResponse:
    status_code = 200

    def json(self):
        return {"standings": [{"table": [{"position": 1}]}]}


class LimitedResponse:
    status_code = 429


def test_cache_avoids_second_request(monkeypatch):
    api._cache.clear()
    calls = []

    def fake_get(*args, **kwargs):
        calls.append(1)
        return FakeResponse()

    monkeypatch.setattr(api.httpx, "get", fake_get)
    api.get_table()
    api.get_table()
    assert len(calls) == 1


def test_rate_limit_raises_api_error(monkeypatch):
    api._cache.clear()
    monkeypatch.setattr(api.httpx, "get", lambda *a, **k: LimitedResponse())
    with pytest.raises(api.APIError) as exc:
        api.get_table()
    assert "limiti" in str(exc.value)
