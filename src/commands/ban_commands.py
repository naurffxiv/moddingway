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
    )
    async def ban(
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str,
    ):
        """Ban the specified user."""
        async with create_response_context(interaction) as response_message:
            (is_banned, is_dm_sent, result_description) = await ban_user(user, reason)

            if is_banned:  # ban succeeded
                if not is_dm_sent:  # dm failed
                    async with create_logging_embed(
                        interaction, user=user, reason=reason, error=result_description
                    ) as logging_embed:
                        response_message.set_string(result_description)
                else:  # ban succeeded, dm failed.
                    async with create_logging_embed(
                        interaction, user=user, reason=reason, result=result_description
                    ) as logging_embed:
                        response_message.set_string(result_description)
            else:  # ban failed, dont create embed
                response_message.set_string(result_description)
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
