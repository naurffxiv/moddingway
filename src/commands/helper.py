import sys
from typing import Optional
import discord
from settings import get_settings
from util import EmbedField, logging_embed_context

settings = get_settings()


def create_logging_embed(interaction: discord.Interaction, **kwargs):
    fields = [EmbedField("Action", f"/{interaction.command.name}")]
    if kwargs is not None:
        for key, value in kwargs.items():
            match (type(value)):
                case discord.Member:
                    fields.append(EmbedField(key.title(), f"<@{value.id}>"))
                case discord.ChannelType:
                    fields.append(EmbedField(key.title(), f"<#{value}>"))
                case _:
                    fields.append(EmbedField(key.title(), value))

    return logging_embed_context(
        interaction.guild.get_channel(settings.logging_channel_id),
        user=interaction.user,
        timestamp=interaction.created_at,
        description=f"Used `{interaction.command.name}` command in {interaction.channel.mention}",
        fields=fields,
    )
