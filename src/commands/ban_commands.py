import discord
from discord.ext.commands import Bot
from settings import get_settings
from services.ban_service import ban_user
from util import is_user_moderator
from .helper import create_logging_embed

settings = get_settings()


def create_ban_commands(bot: Bot) -> None:
    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(
        user="User being banned",
        reason="Reason for ban",
    )
    async def ban(
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str,
    ):
        """Ban the specified user."""
        #result is a tuple of state and descriptio
        result = await ban_user(user, reason)

        if result[0]: #ban succeeded dont create embed.
            if not result[1]: #dm failed 
                async with create_logging_embed(
                    interaction, user=user, reason=reason, error = result[2]
                ) as logging_embed:
                    await interaction.response.send_message(result[2], ephemeral=True)
            else: #ban succeeded, dm failed. 
                async with create_logging_embed(
                    interaction, user=user, reason=reason, result = result[2]
                ) as logging_embed:
                    await interaction.response.send_message(result[2], ephemeral=True)
        else: #ban failed, dont create embed
            await interaction.response.send_message(result[2], ephemeral=True)
