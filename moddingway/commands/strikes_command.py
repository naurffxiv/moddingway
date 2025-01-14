import logging

import discord
from discord.ext.commands import Bot

from moddingway.enums import Role, StrikeSeverity
from moddingway.services import strike_service
from moddingway.util import is_user_moderator, user_has_role

from .helper import create_logging_embed, create_response_context

logger = logging.getLogger(__name__)


def create_strikes_commands(bot: Bot) -> None:
    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(user="User being striked")
    async def add_strike(
        interaction: discord.Interaction,
        user: discord.Member,
        severity: StrikeSeverity,
        reason: str,
    ):
        """Add a strike to the user"""
        if user_has_role(user, Role.MOD):
            logger.warning(
                f"{interaction.user.id} used the add strike command on {user.id}, it failed because targeted user is a mod."
            )
            await interaction.response.send_message(
                f"Unable to add strike to {user.mention}: You cannot add strike to a mod.",
                ephemeral=True,
            )
            return
        async with create_response_context(interaction) as response_message:
            async with create_logging_embed(
                interaction, user=user, reason=reason, severity=severity.name
            ) as logging_embed:
                await strike_service.add_strike(
                    logging_embed, user, severity, reason, interaction.user
                )

                response_message.set_string(
                    f"Successfully added strike to {user.mention}"
                )

    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(user="User whose strikes you are viewing")
    async def view_strikes(interaction: discord.Interaction, user: discord.User):
        """View the strikes of the user"""
        async with create_response_context(interaction) as response_message:
            strike_details = await strike_service.get_user_strikes(user)

            response_message.set_string(strike_details)
