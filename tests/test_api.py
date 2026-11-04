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


def _count(result):
    from prometheus_client import REGISTRY

    value = REGISTRY.get_sample_value("goalzone_api_requests_total", {"result": result})
    return value or 0


def test_metrics_count_ok_and_cache_hit(monkeypatch):
    api._cache.clear()
    monkeypatch.setattr(api.httpx, "get", lambda *a, **k: FakeResponse())
    ok_before, hit_before = _count("ok"), _count("cache_hit")
    api.get_table()
    api.get_table()
    assert _count("ok") == ok_before + 1
    assert _count("cache_hit") == hit_before + 1


def test_metrics_count_rate_limited(monkeypatch):
    api._cache.clear()
    monkeypatch.setattr(api.httpx, "get", lambda *a, **k: LimitedResponse())
    before = _count("rate_limited")
    with pytest.raises(api.APIError):
        api.get_table()
    assert _count("rate_limited") == before + 1
