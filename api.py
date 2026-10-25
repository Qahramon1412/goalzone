from datetime import date

import httpx

from config import FOOTBALL_DATA_TOKEN

BASE_URL = "https://api.football-data.org/v4"


class APIError(Exception):
    """API xatosi. Matni foydalanuvchiga ko'rsatiladi."""


def _get(path):
    headers = {"X-Auth-Token": FOOTBALL_DATA_TOKEN}
    try:
        response = httpx.get(f"{BASE_URL}{path}", headers=headers, timeout=10)
    except httpx.RequestError:
        raise APIError("Server bilan aloqa yo'q. Birozdan keyin urinib ko'ring.")
    if response.status_code == 429:
        raise APIError("So'rovlar limiti tugadi. Bir daqiqadan keyin urinib ko'ring.")
    if response.status_code != 200:
        raise APIError(f"API xatosi ({response.status_code}). Keyinroq urinib ko'ring.")
    return response.json()


def get_table():
    data = _get("/competitions/PL/standings")
    return data["standings"][0]["table"]


def get_today():
    today = date.today().isoformat()
    data = _get(f"/competitions/PL/matches?dateFrom={today}&dateTo={today}")
    return data["matches"]
