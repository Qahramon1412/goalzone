import asyncio

from prometheus_client import REGISTRY

from metrics import track


def _count(command):
    value = REGISTRY.get_sample_value("goalzone_commands_total", {"command": command})
    return value or 0


def test_track_counts_and_calls_handler():
    calls = []

    async def handler(update, context):
        calls.append(1)
        return "ok"

    wrapped = track("testcmd")(handler)
    before = _count("testcmd")
    result = asyncio.run(wrapped(None, None))

    assert result == "ok"
    assert calls == [1]
    assert _count("testcmd") == before + 1


def test_counters_are_predeclared():
    for command in ("start", "my"):
        assert (
            REGISTRY.get_sample_value("goalzone_commands_total", {"command": command})
            is not None
        )
