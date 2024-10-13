import sys
from typing import Optional
import discord
from settings import get_settings
from util import EmbedField, logging_embed_context

settings = get_settings()


def create_logging_embed(interaction: discord.Interaction, args: Optional[dict] = None):
    fields = [EmbedField("Action", f"/{interaction.command.name}")]
    if args is not None:
        for key, value in args.items():
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


def get_args():
    """Returns all arguments in the calling function except the first one (interaction)"""
    calling_frame = sys._getframe().f_back
    caller = calling_frame.f_code
    relevant_vars = caller.co_varnames[: caller.co_argcount]
    return {name: calling_frame.f_locals[name] for name in relevant_vars[1:]}
