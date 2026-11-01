import asyncio
import logging
import pathlib

logger = logging.getLogger(__name__)

HEARTBEAT_FILE = pathlib.Path("/tmp/heartbeat")
INTERVAL = 60  # soniya


async def heartbeat(bot):
    while True:
        try:
            await bot.get_me()
            HEARTBEAT_FILE.touch()
        except Exception:
            logger.exception("Health check: Telegram bilan aloqa yo'q")
        await asyncio.sleep(INTERVAL)
