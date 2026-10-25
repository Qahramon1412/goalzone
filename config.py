import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
FOOTBALL_DATA_TOKEN = os.getenv("FOOTBALL_DATA_TOKEN")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "goalzone")
DB_USER = os.getenv("DB_USER", "goalzone")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def check_config():
    if not TELEGRAM_BOT_TOKEN:
        raise SystemExit("Xato: .env faylida TELEGRAM_BOT_TOKEN yo'q")
    if not FOOTBALL_DATA_TOKEN:
        raise SystemExit("Xato: .env faylida FOOTBALL_DATA_TOKEN yo'q")
    if not DB_PASSWORD:
        raise SystemExit("Xato: .env faylida DB_PASSWORD yo'q")
