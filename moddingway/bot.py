import logging

import discord
from discord.ext.commands import Bot

from moddingway import workers
from moddingway.commands.ban_commands import create_ban_commands
from moddingway.commands.exile_commands import create_exile_commands
from moddingway.commands.helper import create_bot_errors
from moddingway.commands.slowmode_commands import create_slowmode_commands
from moddingway.commands.strikes_command import create_strikes_commands
from moddingway.commands.note_commands import create_note_commands
from moddingway.commands.warning_commands import create_warning_commands
from moddingway.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class ModdingwayBot(Bot):
    async def setup_hook(self):
        self._register_commands()

        guild = discord.Object(id=settings.guild_id)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        logger.info("Syncing settings to guild completed")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        workers.start_tasks(self)

    def _register_commands(self):
        logger.info("Starting registering commands")
        create_exile_commands(self)
        create_ban_commands(self)
        create_slowmode_commands(self)
        create_strikes_commands(self)
        create_note_commands(self)
        create_bot_errors(self)
        create_warning_commands(self)
        logger.info("Registering commands finished")
