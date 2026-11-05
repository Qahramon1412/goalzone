import functools

from prometheus_client import Counter, Gauge, start_http_server

COMMANDS = Counter("goalzone_commands_total", "Bot commands handled", ["command"])
API_REQUESTS = Counter(
    "goalzone_api_requests_total",
    "football-data.org requests by result",
    ["result"],
)
HEARTBEAT = Gauge(
    "goalzone_last_heartbeat_timestamp_seconds",
    "Unix time of the last successful Telegram check",
)


def track(command):
    """Buyruq handlerini o'rab, har chaqirilganda hisoblaydi."""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(update, context):
            COMMANDS.labels(command).inc()
            return await func(update, context)

        return wrapper

    return decorator


def start_metrics_server(port=8000):
    start_http_server(port)


# Hisoblagichlarni nol bilan oldindan e'lon qilamiz, shunda ular
# birinchi ishlatilishdan oldin ham Prometheus'da ko'rinadi.
for _command in ("start", "today", "table", "fixtures", "favorite", "my"):
    COMMANDS.labels(_command)
for _result in ("ok", "cache_hit", "rate_limited", "error"):
    API_REQUESTS.labels(_result)
