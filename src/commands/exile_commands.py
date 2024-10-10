import discord
from discord.ext.commands import Bot
from settings import get_settings
from services.exile_service import exile_user, unexile_user
from util import is_user_moderator, calculate_time_delta
from typing import Optional
from .helper import create_logging_embed, get_args

settings = get_settings()


def create_exile_commands(bot: Bot) -> None:
    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(user="User being exiled")
    async def unexile(interaction: discord.Interaction, user: discord.Member):
        """Unexile the specified user."""

        async with create_logging_embed(interaction, get_args()) as logging_embed:
            error_message = await unexile_user(logging_embed, user)

            await interaction.response.send_message(
                error_message or f"Successfully unexiled {user.mention}", ephemeral=True
            )

    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(
        user="User being exiled",
        duration="The duration of the exile. TBA format",
        reason="Reason for exile",
    )
    async def exile(
        interaction: discord.Interaction,
        user: discord.Member,
        duration: Optional[str],
        reason: str,
    ):
        """Exile the specified user."""
        async with create_logging_embed(interaction, get_args()) as logging_embed:
            exile_duration = calculate_time_delta(duration)
            if duration and not exile_duration:
                await interaction.response.send_message(
                    "Invalid exile duration given, duration should be in the form of [1 or 2 digits][s, d, m, h]",
                    ephemeral=True,
                )
                return

            error_message = await exile_user(
                logging_embed, user, exile_duration, reason
            )

            await interaction.response.send_message(
                error_message or f"Successfully exiled {user.mention}", ephemeral=True
            )
