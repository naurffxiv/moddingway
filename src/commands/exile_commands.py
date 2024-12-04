import discord
import logging
from discord.ext.commands import Bot
from settings import get_settings
from services.exile_service import (
    exile_user,
    unexile_user,
    get_user_exiles,
    get_active_exiles,
    format_time_string,
)
from util import is_user_moderator, calculate_time_delta, user_has_role
from typing import Optional
from .helper import create_logging_embed, create_response_context
from random import choice
import datetime
from enums import Role

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
        duration: str,
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
        if user_has_role(user, Role.MOD):
            logger.warning(
                f"{interaction.user.id} used the exile command on {user.id}, it failed because targeted user is a mod."
            )
            await interaction.response.send_message(
                f"Unable to exile {user.mention}: You cannot exile a mod.",
                ephemeral=True,
            )
            return
        start_timestamp = datetime.datetime.now(datetime.timezone.utc)
        end_timestamp = start_timestamp + exile_duration
        async with create_response_context(interaction) as response_message:
            async with create_logging_embed(
                interaction,
                user=user,
                duration=format_time_string(duration),
                reason=reason,
                expiration=end_timestamp,
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
        safety_options = [True, True, True, True, True, False]
        exile_duration_options = [1, 6, 12, 18, 24]
        safety_choice = choice(safety_options)
        duration_choice = choice(exile_duration_options)
        duration_string = f"{duration_choice}hour"
        start_timestamp = datetime.datetime.now(datetime.timezone.utc)
        end_timestamp = start_timestamp + calculate_time_delta(duration_string)

        if safety_choice:
            await interaction.response.send_message(
                f"<@{interaction.user.id}> has tested their luck and lives another day...",
                ephemeral=False,
            )
            return
        if user_has_role(interaction.user, Role.MOD):
            await interaction.response.send_message(
                f"<@{interaction.user.id}> has tested their luck and has utterly failed! <@{interaction.user.id}> has been sent into exile for {duration_choice} hour(s).",
                ephemeral=False,
            )
            return
        async with create_response_context(interaction, False) as response_message:
            async with create_logging_embed(
                interaction,
                duration=format_time_string(duration_string),
                expiration=end_timestamp,
            ) as logging_embed:
                reason = "roulette"
                exile_duration = calculate_time_delta(duration_string)
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
                        f"<@{interaction.user.id}> has tested their luck and has utterly failed! <@{interaction.user.id}> has been sent into exile for {duration_choice} hour(s)."
                    )

    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(user="User whose logged exile are being viewed")
    async def view_logged_exiles(
        interaction: discord.Interaction, user: discord.Member
    ):
        """View logged exiles of a user."""

        async with create_response_context(interaction) as response_message:
            try:
                msg = await get_user_exiles(user)
                response_message.set_string(msg)
            except Exception as e:
                logger.error(f"Error in get_user_exiles: {str(e)}")
                async with create_logging_embed(interaction, user=user, error=str(e)):
                    response_message.set_string(
                        "An error occurred while fetching user exiles."
                    )

    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    async def view_active_exiles(interaction: discord.Interaction):
        """View all active exiles for all users."""

        async with create_response_context(interaction) as response_message:
            msg = await get_active_exiles()

            response_message.set_string(msg)
