import logging

import discord
from discord.ext.commands import Bot

from moddingway.constants import Role
from moddingway.services.ban_service import ban_member, ban_user
from moddingway.settings import get_settings
from moddingway.util import is_user_moderator, user_has_role

from .helper import create_logging_embed, create_response_context

settings = get_settings()

logger = logging.getLogger(__name__)


def create_ban_commands(bot: Bot) -> None:
    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(
        user="User being banned",
        reason="Reason for ban",
        delete_messages="Whether messages from the banned user should be deleted or not",
    )
    async def ban(
        interaction: discord.Interaction,
        user: (
            discord.User | discord.Member
        ),  # Normally accepts members, need to accept users too in case we need to ban by id
        reason: str,
        delete_messages: bool = False,  # Default to false for no message deletion as we typically don't want to delete messages.
    ):
        # sanity check just in case
        if isinstance(user, discord.User):
            member = interaction.guild.get_member(user.id)
            if member is not None:
                user = member

        if isinstance(user, discord.Member):
            if user_has_role(user, Role.MOD):
                logger.warning(
                    f"{interaction.user.id} used the ban command on {user.id}, it failed because targeted user is a mod."
                )
                await interaction.response.send_message(
                    f"Unable to ban {user.mention}: You cannot ban a mod.",
                    ephemeral=True,
                )
                return

        """Ban the specified user."""
        async with create_response_context(interaction) as response_message:
            if isinstance(user, discord.User):
                ban_success, error = await ban_user(
                    interaction, user, reason, delete_messages
                )
            else:
                ban_success, error = await ban_member(user, reason, delete_messages)
            async with create_logging_embed(
                interaction,
                user=user,
                reason=reason,
                delete_messages=delete_messages,
            ) as logging_embed:
                if ban_success:
                    success_str = f"Successfully banned {user.mention}."
                    logging_embed.add_field(
                        name="Result", value=success_str, inline=False
                    )
                    response_message.set_string(success_str)
                    if error:
                        logging_embed.add_field(
                            name="DM Status", value=error, inline=False
                        )
                else:
                    logging_embed.add_field(name="Error", value=error, inline=False)
                    response_message.set_string(error)
