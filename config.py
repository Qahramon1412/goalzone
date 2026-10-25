import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
FOOTBALL_DATA_TOKEN = os.getenv("FOOTBALL_DATA_TOKEN")


def check_config():
    if not TELEGRAM_BOT_TOKEN:
        raise SystemExit("Xato: .env faylida TELEGRAM_BOT_TOKEN yo'q")
    if not FOOTBALL_DATA_TOKEN:
        raise SystemExit("Xato: .env faylida FOOTBALL_DATA_TOKEN yo'q")
