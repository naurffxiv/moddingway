import discord
from discord.ext.commands import Bot
from settings import get_settings
from commands.exile_commands import create_exile_commands
from commands.ban_commands import create_ban_commands
import logging
import tasks

settings = get_settings()
logger = logging.getLogger(__name__)


class ModdingwayBot(Bot):
    async def setup_hook(self):
        self._register_commands()

        guild = discord.Object(id=settings.guild_id)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        tasks.start_tasks(self)

    def _register_commands(self):
        create_exile_commands(self)
        create_ban_commands(self)
