import discord
from discord.ext.commands import Bot
from settings import get_settings
from services.ban_service import ban_user
from util import is_user_moderator
from .helper import create_logging_embed, create_response_context

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
        # result is a tuple of ban state (bool), dm state (bool), and description of rersults
        (ban_state, dm_state, result_description) = await ban_user(user, reason)

        if ban_state:  # ban succeeded
            if not dm_state:  # dm failed
                async with create_logging_embed(
                    interaction, user=user, reason=reason, error=result_description
                ) as logging_embed:
                    await interaction.response.send_message(
                        result_description, ephemeral=True
                    )
            else:  # ban succeeded, dm failed.
                async with create_logging_embed(
                    interaction, user=user, reason=reason, result=result_description
                ) as logging_embed:
                    await interaction.response.send_message(
                        result_description, ephemeral=True
                    )
        else:  # ban failed, dont create embed
            await interaction.response.send_message(result_description, ephemeral=True)
