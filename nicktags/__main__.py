import asyncio
import os
import signal
import sys

import disnake
from loguru import logger

from nicktags.bot import Nick
from nicktags.constants import Config
from nicktags.database import DB

_intents = disnake.Intents.none()
_intents.guilds = True
_intents.members = True


async def main() -> None:
    """Create and run the bot"""

    bot: Nick = Nick(intents=_intents, reload=True)

    # setup bot class variables
    bot.db = DB()
    bot.start_time = disnake.utils.utcnow()

    try:
        bot.load_extensions()
    except Exception:
        await bot.close()
        raise

    logger.info("Bot is starting...")

    if os.name != "nt":
        # start process for linux based OS (Docker)

        loop = asyncio.get_event_loop()

        future = asyncio.ensure_future(bot.start(Config.token or ""), loop=loop)
        loop.add_signal_handler(signal.SIGINT, lambda: future.cancel())
        loop.add_signal_handler(signal.SIGTERM, lambda: future.cancel())

        try:
            await future
        except asyncio.CancelledError:

            logger.warning("Kill command was sent to the bot. Closing bot and event loop")
            if not bot.is_closed():
                await bot.close()
    else:
        await bot.start(Config.token)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
