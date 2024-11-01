from datetime import datetime
import discord
from discord.ext.commands import Bot
from settings import get_settings
from util import create_interaction_embed_context
from typing import Optional

settings = get_settings()


def create_autounexile_embed(
    self, user: discord.User, exile_id: str, end_timestamp: str
):
    return create_interaction_embed_context(
        self.get_channel(settings.logging_channel_id),
        user=user,
        timestamp=end_timestamp,
        description=f"<@{user.id}>'s exile has timed out",
        footer=f"Exile ID: {exile_id}",
    )


def create_automod_embed(self, thread: discord.Thread, timestamp: datetime):
    return create_interaction_embed_context(
        self.get_channel(settings.logging_channel_id),
        user=thread.owner,
        timestamp=timestamp,
        description=f'<@{thread.owner_id}>\'s thread, "{thread.name}", meets the requirements for automod deletion.',
    )
