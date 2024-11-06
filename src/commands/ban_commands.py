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
        async with create_response_context(interaction) as response_message:
            async with create_logging_embed(
                interaction, user=user, reason=reason
            ) as logging_embed:
                await ban_user(logging_embed, user, reason)

                response_message.set_string(f"Successfully banned {user.mention}")
