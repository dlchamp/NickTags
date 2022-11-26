import os
from datetime import datetime
from sys import version as sys_version

import disnake
from disnake import __version__ as disnake_version
from disnake.ext import commands
from loguru import logger

from nicktags import __version__ as bot_version
from nicktags.database import DB

__all__ = ("Nick",)


class Nick(commands.InteractionBot):
    """Base bot instance"""

    db: DB
    start_time: datetime

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    async def on_ready(self) -> None:

        print(
            "----------------------------------------------------------------------\n"
            f'Bot started at: {datetime.now().strftime("%m/%d/%Y - %H:%M:%S")}\n'
            f"System Version: {sys_version}\n"
            f"Disnake Version: {disnake_version}\n"
            f"Bot Version: {bot_version}\n"
            f"Connected to Discord as {self.user} ({self.user.id})\n"
            "----------------------------------------------------------------------\n"
        )

    def load_extensions(self) -> None:
        """Load all extensions available on 'cogs'"""
        for item in os.listdir("nicktags/cogs"):
            if "__" in item or not item.endswith("py"):
                continue

            ext = f"nicktags.cogs.{item[:-3]}"
            self.load_extension(ext)
            logger.info(f"Cog loaded: {ext}")
