import logging

import discord
from discord.ext.commands import Bot

from moddingway.settings import get_settings
from moddingway.util import is_user_moderator, log_info_and_add_field
from moddingway.workers.forum_automod import (
    autodelete_threads,
    autodelete_event_threads,
)

from .helper import create_logging_embed, create_response_context

settings = get_settings()
logger = logging.getLogger(__name__)


def create_forum_commands(bot: Bot) -> None:

    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    async def run_automod(interaction: discord.Interaction):
        """Run the forum automod task manually."""

        async with create_response_context(interaction) as response_message:
            async with create_logging_embed(
                interaction,
            ) as logging_embed:
                result = await autodelete_threads(bot)
                log_info_and_add_field(logging_embed, logger, "Result", result)
            response_message.set_string(result)

    @bot.tree.command()
    @discord.app_commands.check(is_user_moderator)
    async def run_event_automod(interaction: discord.Interaction):
        """Run the event forum automod task manually."""

        async with create_response_context(interaction) as response_message:
            async with create_logging_embed(
                interaction,
            ) as logging_embed:
                result = await autodelete_event_threads(bot)
                log_info_and_add_field(logging_embed, logger, "Result", result)
            response_message.set_string(result)
