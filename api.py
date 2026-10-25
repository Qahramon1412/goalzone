import time
from datetime import date, timedelta

import httpx

from config import FOOTBALL_DATA_TOKEN

BASE_URL = "https://api.football-data.org/v4"
CACHE_TTL = 60  # soniya

_cache = {}


class APIError(Exception):
    """API xatosi. Matni foydalanuvchiga ko'rsatiladi."""


def _get(path):
    now = time.monotonic()
    cached = _cache.get(path)
    if cached and now - cached[0] < CACHE_TTL:
        return cached[1]

    headers = {"X-Auth-Token": FOOTBALL_DATA_TOKEN}
    try:
        response = httpx.get(f"{BASE_URL}{path}", headers=headers, timeout=10)
    except httpx.RequestError:
        raise APIError("Server bilan aloqa yo'q. Birozdan keyin urinib ko'ring.")
    if response.status_code == 429:
        raise APIError("So'rovlar limiti tugadi. Bir daqiqadan keyin urinib ko'ring.")
    if response.status_code != 200:
        raise APIError(f"API xatosi ({response.status_code}). Keyinroq urinib ko'ring.")

    data = response.json()
    _cache[path] = (now, data)
    return data
import time
from datetime import date, timedelta

import httpx

from config import FOOTBALL_DATA_TOKEN

BASE_URL = "https://api.football-data.org/v4"
CACHE_TTL = 60  # soniya

_cache = {}


class APIError(Exception):
    """API xatosi. Matni foydalanuvchiga ko'rsatiladi."""


def _get(path):
    now = time.monotonic()
    cached = _cache.get(path)
    if cached and now - cached[0] < CACHE_TTL:
        return cached[1]

    headers = {"X-Auth-Token": FOOTBALL_DATA_TOKEN}
    try:
        response = httpx.get(f"{BASE_URL}{path}", headers=headers, timeout=10)
    except httpx.RequestError:
        raise APIError("Server bilan aloqa yo'q. Birozdan keyin urinib ko'ring.")
    if response.status_code == 429:
        raise APIError("So'rovlar limiti tugadi. Bir daqiqadan keyin urinib ko'ring.")
    if response.status_code != 200:
        raise APIError(f"API xatosi ({response.status_code}). Keyinroq urinib ko'ring.")

    data = response.json()
    _cache[path] = (now, data)
    return data


def get_table():
    data = _get("/competitions/PL/standings")
    return data["standings"][0]["table"]


def get_today():
    today = date.today().isoformat()
    data = _get(f"/competitions/PL/matches?dateFrom={today}&dateTo={today}")
    return data["matches"]


def get_fixtures(days=7):
    start = (date.today() + timedelta(days=1)).isoformat()
    end = (date.today() + timedelta(days=days)).isoformat()
    data = _get(f"/competitions/PL/matches?dateFrom={start}&dateTo={end}")
    return data["matches"]
