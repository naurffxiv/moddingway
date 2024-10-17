import sys
from typing import Optional
import discord
from discord.ext.commands import Bot
from settings import get_settings
from util import EmbedField, create_interaction_embed_context

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

    return create_interaction_embed_context(
        interaction.guild.get_channel(settings.logging_channel_id),
        user=interaction.user,
        timestamp=interaction.created_at,
        description=f"Used `{interaction.command.name}` command in {interaction.channel.mention}",
        fields=fields,
    )


def create_bot_errors(bot: Bot) -> None:
    @bot.tree.error
    async def on_app_command_error(interaction: discord.Interaction, error):
        # Check if the error is due to a cooldown
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            hours_left = int(error.retry_after / 3600)
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {hours_left} hour(s).",
                ephemeral=True,
            )
        else:
            # Handle other errors if necessary
            await interaction.response.send_message(
                "An error occurred while processing the command.", ephemeral=True
            )
