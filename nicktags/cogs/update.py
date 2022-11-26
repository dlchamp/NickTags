from datetime import datetime, timedelta

import disnake
from disnake.ext import commands
from loguru import logger

from nicktags.bot import Nick


class Update(commands.Cog):
    def __init__(self, bot: Nick) -> None:
        self.bot = bot
        self.recent = {}

    def get_highest_role_with_tag(self, roles: list[disnake.Role]) -> disnake.Role:
        """Get the highest role that has a configured tag, and return the `disnake.Role`"""
        roles = sorted(roles, reverse=True)
        # add tags if, available to the roles
        for role in roles:
            tag = self.bot.db.get_tag_by_role(role)
            if tag is None:
                continue

            return tag

    @commands.Cog.listener()
    async def on_member_update(self, before: disnake.Member, after: disnake.Member) -> None:
        """Function is called when a member update event has fired. Any of the following changes
        will fire this event

        - avatar
        - current_timeout
        - nickname
        - pending
        - premium_since
        - roles
        """
        now = datetime.now()

        if len(before.roles) != len(after.roles) or before.nick != after.nick:

            if after.id in self.recent.keys():
                if now < self.recent[after.id]:
                    return

            self.recent[after.id] = now + timedelta(seconds=1)
            return await self.add_update_tag(after)

    async def add_update_tag(self, member: disnake.Member) -> None:
        """A new role was granted, so we want to check if we need to update the tag"""

        tag = self.get_highest_role_with_tag(member.roles)
        nick = member.display_name
        split_nick = nick.split(" ", maxsplit=1)

        if len(split_nick) == 1:

            if tag is None:
                return

            nick = f"[{tag}] {nick}"

        else:
            if split_nick[0].startswith("[") and tag is None:
                nick = split_nick[1]

            elif split_nick[0].startswith("[") and tag:
                nick = f"[{tag}] {split_nick[1]}"

            else:
                nick = " ".join(split_nick)

        try:
            await member.edit(nick=nick)
        except disnake.Forbidden:
            logger.warning("Role change detected | Member is owner. Unable to update nickname")


def setup(bot: Nick) -> None:
    bot.add_cog(Update(bot))
