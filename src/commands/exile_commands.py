import discord
import logging
from discord.ext.commands import Bot
from settings import get_settings
from services.exile_service import exile_user, unexile_user, get_user_exiles
from util import is_user_moderator, calculate_time_delta
from typing import Optional
from .helper import create_logging_embed, create_response_context
from random import choice

settings = get_settings()
logger = logging.getLogger(__name__)


def create_exile_commands(bot: Bot) -> None:
    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(user="User being exiled")
    async def unexile(interaction: discord.Interaction, user: discord.Member):
        """Unexile the specified user."""

        async with create_response_context(interaction) as response_message:
            async with create_logging_embed(interaction, user=user) as logging_embed:
                error_message = await unexile_user(logging_embed, user)

                response_message.set_string(
                    error_message or f"Successfully unexiled {user.mention}"
                )

    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(
        user="User being exiled",
        duration="Enter a value between 1 and 99 followed by sec, min, hour, or day. Examples: 1sec, 1min, 1hour, 1day.",
        reason="Reason for exile",
    )
    async def exile(
        interaction: discord.Interaction,
        user: discord.Member,
        duration: Optional[str],
        reason: str,
    ):
        """Exile the specified user."""
        exile_duration = calculate_time_delta(duration)
        if duration and not exile_duration:
            await interaction.response.send_message(
                "Invalid exile duration given, duration should be in the form value between 1 and 99 followed by sec, min, hour, or day. Examples: 1sec, 1min, 1hour, 1day. No action will be taken",
                ephemeral=True,
            )
            return

        async with create_response_context(interaction) as response_message:
            async with create_logging_embed(
                interaction, user=user, duration=duration, reason=reason
            ) as logging_embed:

                error_message = await exile_user(
                    logging_embed, user, exile_duration, reason
                )

                response_message.set_string(
                    error_message or f"Successfully exiled {user.mention}"
                )

    @bot.tree.command()
    @discord.app_commands.checks.cooldown(
        1, 86400, key=lambda i: (i.guild_id, i.user.id)
    )
    async def roulette(interaction: discord.Interaction):
        """Test your luck, fail and be exiled..."""
        exile_duration_options = [0, 1, 6, 12, 18, 24]
        rand_choice = choice(exile_duration_options)

        async with create_response_context(interaction, False) as response_message:
            async with create_logging_embed(interaction) as logging_embed:
                if rand_choice != 0:
                    reason = "roulette"
                    exile_duration = calculate_time_delta(f"{rand_choice}h")
                    error_message = await exile_user(
                        logging_embed, interaction.user, exile_duration, reason
                    )

                    if error_message:
                        logger.error(f"An error occurred: {error_message}")
                        response_message.set_string(
                            "An error occurred while processing the command."
                        )
                        return
                    else:
                        response_message.set_string(
                            f"<@{interaction.user.id}> has tested their luck and has utterly failed! <@{interaction.user.id}> has been sent into exile for {rand_choice} hour(s)."
                        )
                else:
                    response_message.set_string(
                        f"<@{interaction.user.id}> has tested their luck and lives another day..."
                    )

    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(user="User whose exile is being checked")
    async def check_exile(interaction: discord.Interaction, user: discord.Member):
        """Check the exile status of a user."""

        async with create_response_context(interaction) as response_message:
            async with create_logging_embed(interaction, user=user) as logging_embed:
                msg = await get_user_exiles(logging_embed, user)

                response_message.set_string(msg)
