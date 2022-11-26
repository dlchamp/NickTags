import disnake
from disnake.ext import commands

from nicktags.bot import Nick


class Admin(
    commands.Cog,
    slash_command_attrs={
        "dm_permission": False,
        "default_member_permissions": disnake.Permissions(administrator=True),
    },
):
    def __init__(self, bot: Nick) -> None:
        self.bot = bot

    @commands.slash_command(name="tag")
    async def tag(self, inter: disnake.AppCmdInter) -> None:
        """Slash command parent.  Always invoked with child command"""
        pass

    @tag.sub_command(name="add")
    async def tag_add(self, inter: disnake.AppCmdInter, role: disnake.Role, tag: str) -> None:
        """Create a new tag for a role

        Parameters
        -----------
        role: :type:`disnake.Role`
            Select the role you wish to add the tag to
        tag: :type:`str`
            Input the nickname tag for this role. ( [] will be added automatically so do not include them )
        """

        _role_id, _tag = self.bot.db.get_tag_named(tag)

        if _tag:
            role = inter.guild.get_role(int(_role_id))
            return await inter.response.send_message(
                f"**{tag}** is already in use for {role.mention}.  Please create a new tag, or edit the existing tag for {role.mention}",
                ephemeral=True,
            )

        self.bot.db.add_update_tag(role.id, tag)
        await inter.response.send_message(
            f"{tag} has been created for {role.mention}", ephemeral=True
        )

    @tag.sub_command(name="edit")
    async def tag_edit(self, inter: disnake.AppCmdInter, tag: str, new_tag: str) -> None:
        """Edit an existing tag

        Parameters
        ----------
        tag: :type:`str`
            Select a tag to edit
        """

        _role_id, tag = self.bot.db.get_tag_named(tag.split(" (")[0])

        if not _role_id:
            return await inter.response.send_message(
                "Could not find a role with the associated tag: {tag}", ephemeral=True
            )

        role = inter.guild.get_role(int(_role_id))

        self.bot.db.add_update_tag(_role_id, new_tag)
        await inter.response.send_message(
            f"Tag for {role.mention} has been updated to [{new_tag}]", ephemeral=True
        )

    @tag.sub_command(name="delete")
    async def tag_delete(self, inter: disnake.AppCmdInter, tag: str) -> None:
        """Delete a tag.

        Parameters
        ----------
        tag: :type:`str`
            Select a tag to delete"""

        _role_id, _tag = self.bot.db.get_tag_named(tag.split(" (")[0])

        if _tag is None:
            return await inter.response.send_message(
                f"Unable to find a configured tag with name: {tag}", ephemeral=True
            )

        role = inter.guild.get_role(int(_role_id))
        self.bot.db.delete_tag(_tag)
        await inter.response.send_message(
            f"Tag ({tag}) for {role.mention} has been deleted", ephemeral=True
        )

    @tag_edit.autocomplete("tag")
    @tag_delete.autocomplete("tag")
    async def tag_autocomplete(self, interaction: disnake.AppCmdInter, tag: str) -> list[str]:
        data = self.bot.db.load_data()
        tag = tag.lower()
        tags = [f"{v} ({interaction.guild.get_role(int(k)).name})" for k, v in data.items()]
        return [t for t in tags if tag in t.lower()]


def setup(bot: Nick) -> None:
    bot.add_cog(Admin(bot))
