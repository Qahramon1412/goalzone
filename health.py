import asyncio
import logging
import pathlib

from metrics import HEARTBEAT

logger = logging.getLogger(__name__)

HEARTBEAT_FILE = pathlib.Path("/tmp/heartbeat")
INTERVAL = 60  # soniya


async def heartbeat(bot):
    while True:
        try:
            await bot.get_me()
            HEARTBEAT_FILE.touch()
            HEARTBEAT.set_to_current_time()
        except Exception:
            logger.exception("Health check: Telegram bilan aloqa yo'q")
        await asyncio.sleep(INTERVAL)
