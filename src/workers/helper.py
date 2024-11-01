import discord
from discord.ext.commands import Bot
from settings import get_settings
from util import create_interaction_embed_context

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
