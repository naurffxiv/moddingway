import discord
from discord.ext.commands import Bot
from util import is_user_moderator
from enums import StrikeSeverity


def create_strikes_commands(bot: Bot) -> None:
    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(user="User being exiled")
    async def add_strike(
        interaction: discord.Interaction,
        user: discord.Member,
        severity: StrikeSeverity,
        reason: str,
    ):
        """Add a strike to the user"""
        await interaction.response.send_message("This command is not currently implemented", ephemeral=True)
