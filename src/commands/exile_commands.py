import discord
import logging
from discord.ext.commands import Bot
from settings import get_settings
from services.exile_service import exile_user, unexile_user
from util import is_user_moderator, calculate_time_delta
from typing import Optional
from .helper import create_logging_embed
from random import choice

settings = get_settings()
logger = logging.getLogger(__name__)


def create_exile_commands(bot: Bot) -> None:
    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(user="User being exiled")
    async def unexile(interaction: discord.Interaction, user: discord.Member):
        """Unexile the specified user."""

        async with create_logging_embed(interaction) as logging_embed:
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

        async with create_logging_embed(interaction) as logging_embed:
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

    @bot.tree.command()
    @discord.app_commands.checks.cooldown(
        1, 86400, key=lambda i: (i.guild_id, i.user.id)
    )
    async def roulette(interaction: discord.Interaction):
        """Test your luck, fail and be exiled..."""
        exile_duration_options = [0, 1, 6, 12, 18, 24]
        rand_choice = choice(exile_duration_options)

        async with create_logging_embed(interaction) as logging_embed:
            if rand_choice != 0:
                reason = "roulette"
                exile_duration = calculate_time_delta(f"{rand_choice}h")
                error_message = await exile_user(
                    logging_embed, interaction.user, exile_duration, reason
                )

                if error_message:
                    logger.error(f"An error occurred: {error_message}")
                    await interaction.response.send_message(
                        "An error occurred while processing the command.",
                        ephemeral=True,
                    )
                    return
                else:
                    await interaction.response.send_message(
                        f"<@{interaction.user.id}> has tested their luck and has utterly failed! <@{interaction.user.id}> has been sent into exile for {rand_choice} hour(s).",
                        ephemeral=False,
                    )
            else:
                await interaction.response.send_message(
                    f"<@{interaction.user.id}> has tested their luck and lives another day...",
                    ephemeral=False,
                )

    @bot.tree.error
    async def on_app_command_error(interaction: discord.Interaction, error):
        # Check if the error is due to a cooldown
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            hours_left = int(error.retry_after / 3600)
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {hours_left} hour(s).",
                ephemeral=True,
            )
        else:
            # Handle other errors if necessary
            await interaction.response.send_message(
                "An error occurred while processing the command.", ephemeral=True
            )
