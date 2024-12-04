import discord
from discord.ext.commands import Bot

from moddingway.services.ban_service import ban_user
from moddingway.settings import get_settings
from moddingway.util import is_user_moderator

from .helper import create_logging_embed, create_response_context

settings = get_settings()


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
        user: discord.Member,
        reason: str,
        delete_messages: bool = False,  # Default to false for no message deletion as we typically don't want to delete messages.
    ):
        """Ban the specified user."""
        async with create_response_context(interaction) as response_message:
            ban_success, error = await ban_user(user, reason, delete_messages)
            # Ensure invoking_member has a higher role position than the target user.
            if user.top_role >= interaction.user.top_role:
                response_message.set_string(
                    f"Unable to ban {user.mention}: You cannot ban a user with an equal or higher role than yourself."
                )
                return
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
