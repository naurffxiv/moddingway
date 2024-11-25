import discord
from discord.ext.commands import Bot
from settings import get_settings
from services.ban_service import ban_user
from util import is_user_moderator
from ui import BanModal
from .helper import create_logging_embed, create_response_context

settings = get_settings()


def create_ban_commands(bot: Bot) -> None:
    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    @discord.app_commands.describe(
        user="User being banned",
        reason="Reason for ban",
        delete_messages="Type 'Yes' to delete messages or 'No' to keep them (default: 'No')",
    )
    async def ban(
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str,
        delete_messages: str = "No",  # Default to 'No' for no message deletion
    ):
        """Ban the specified user."""
        # Normalize and validate the input
        delete_messages = delete_messages.strip().capitalize()  # Handle capitalization
        if delete_messages not in ["Yes", "No"]:
            await interaction.response.send_message(
                "Invalid value for 'delete_messages'. Please enter 'Yes' to delete messages or 'No' to keep them.",
                ephemeral=True,
            )
            return

        # Convert delete_messages to a boolean for ban logic
        delete_messages_flag = delete_messages == "Yes"

        async with create_response_context(interaction) as response_message:
            (is_banned, result_description) = await ban_user(
                interaction.user, user, reason, delete_messages_flag
            )

            if is_banned:  # Ban succeeded
                async with create_logging_embed(
                    interaction,
                    user=user,
                    reason=reason,
                    result=result_description,
                    delete_messages_flag=delete_messages_flag,  # Pass as "Yes" or "No"
                ) as logging_embed:
                    response_message.set_string(result_description)
            else:  # Ban failed
                async with create_logging_embed(
                    interaction, user=user, reason=reason, error=result_description
                ) as logging_embed:
                    response_message.set_string(result_description)

    @bot.tree.context_menu(name="Ban User")
    @discord.app_commands.check(is_user_moderator)
    async def ban_user_action(interaction: discord.Interaction, user: discord.Member):
        """Ban the selected user"""
        await interaction.response.send_modal(BanModal(user))

    @bot.tree.context_menu(name="Ban Message Author")
    @discord.app_commands.check(is_user_moderator)
    async def ban_message_author_action(
        interaction: discord.Interaction, message: discord.Message
    ):
        """Ban the user that sent this message"""
        await interaction.response.send_modal(BanModal(message.author))
